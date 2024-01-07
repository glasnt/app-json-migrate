#https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github#connecting_a_github_host_programmatically


# Google Cloud Services to enable
module "project_services" {
  source                      = "terraform-google-modules/project-factory/google//modules/project_services"
  version                     = "14.4.0"
  disable_services_on_destroy = false

  project_id                  = data.google_project.default.project_id
 
  activate_apis = [
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com",
  ]
}

variable "local_filename" { 
  default = "cloudbuild.yaml"
}

variable "region" {
  default = "us-central1"
}

variable "installation_id" {
  # Find from Cloud Build listing on https://github.com/settings/installations 
  description = "ID of the github installation. https://github.com/settings/installations/INSTALLATION_ID"
}

variable "github_repo" {
  description = "Name of your github repo"
}

variable "github_default_branch" { 
  default = "main"
  description = "branch of repo to attach to" # TODO: use branch from ajm
}

variable "github_token" {
  # Generate at https://github.com/settings/tokens/new
  description = "GitHub token with repo and read:user permissions"
}


data "google_project" "default" {}

// Create a secret containing the personal access token and grant permissions to the Service Agent
resource "google_secret_manager_secret" "default" {
  secret_id = "github_secret_token"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "default" {
  secret      = google_secret_manager_secret.default.id
  secret_data = var.github_token
}


resource "google_secret_manager_secret_iam_member" "default" {
  secret_id = google_secret_manager_secret.default.id

  role   = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:service-${data.google_project.default.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
}

resource "google_cloudbuildv2_connection" "default" {
  location = var.region
  name     = "github_connection"

  github_config {
    app_installation_id = var.installation_id
    authorizer_credential {
      oauth_token_secret_version = google_secret_manager_secret_version.default.id
    }
  }
  depends_on = [google_secret_manager_secret_iam_member.default]
}


resource "google_cloudbuildv2_repository" "default" {
  name              = var.github_repo
  parent_connection = google_cloudbuildv2_connection.default.id
  remote_uri        = "https://github.com/${var.github_repo}.git"
}

resource "google_cloudbuild_trigger" "default" {
  name = replace(var.github_repo, "/", "-") # TODO: make a better reflective name
  location = "us-central1"

  repository_event_config {
    repository = google_cloudbuildv2_repository.default.id
    push {
      branch = "^${var.github_default_branch}$"
    }
  }

  # Borrowed from memes/terraform-google-cloudbuild
  #https://github.com/memes/terraform-google-cloudbuild/pull/62/files#diff-dc46acf24afd63ef8c556b77c126ccc6e578bc87e3aa09a931f33d9bf2532fbb

  dynamic "build" {
    for_each = var.local_filename != null ? [yamldecode(file(var.local_filename))] : []

    content {
      dynamic "step" {
        for_each = try(build.value.steps, [])

        content {
          id               = try(step.value.id, null)
          name             = try(step.value.name, null)
          script           = try(step.value.script, null)
          entrypoint       = try(step.value.entrypoint, null)
          args             = try(step.value.args, [])
          env              = try(step.value.env, [])
          dir              = try(step.value.dir, null)
          secret_env       = try(step.value.secretEnv, [])
          timeout          = try(step.value.timeout, null)
          allow_failure    = try(step.value.allow_failure, null)
          allow_exit_codes = try(step.value.allow_exit_codes, null)
          wait_for         = try(step.value.wait_for, null)
          dynamic "volumes" {
            for_each = try(step.value.volumes, [])

            content {
              name = try(volumes.value.name, null)
              path = try(volumes.value.path, null)
            }
          }
        }
      }

      dynamic "artifacts" {
        for_each = try([build.value.artifacts], [])

        content {
          images = try(artifacts.value.images, [])
          objects {
            location = try(artifacts.value.location, null)
            paths    = try(artifacts.value.paths, null)
            timing   = try(artifacts.value.timing, null)
          }
        }
      }

      dynamic "secret" {
        for_each = try([build.value.secret], [])

        content {
          kms_key_name = try(secret.value.kmsKeyName, null)
          secret_env   = try(secret.value.secretEnv, {})
        }
      }

      dynamic "available_secrets" {
        for_each = try([build.value.availableSecrets], [])

        content {
          dynamic "secret_manager" {
            for_each = try(available_secrets.value.secretManager, [])

            content {
              version_name = try(secret_manager.value.versionName, null)
              env          = try(secret_manager.value.env, null)
            }
          }
        }
      }

      dynamic "options" {
        for_each = try([build.value.options], [])

        content {
          source_provenance_hash  = try(options.value.sourceProvenanceHash, null)
          requested_verify_option = try(options.value.requestedVerifyOption, null)
          machine_type            = try(options.value.machineType, null)
          disk_size_gb            = try(options.value.diskSizeGb, null)
          substitution_option     = try(options.value.substitutionOption, null)
          dynamic_substitutions   = try(options.value.dynamicSubstitutions, null)
          log_streaming_option    = try(options.value.logStreamingOption, null)
          worker_pool             = try(options.value.pool, null)
          logging                 = try(options.value.logging, null)
          env                     = try(options.value.env, null)
          secret_env              = try(options.value.secretEnv, [])

          dynamic "volumes" {
            for_each = try(options.value.volumes, [])

            content {
              name = try(volumes.value.name, null)
              path = try(volumes.value.path, null)
            }
          }  
        }
      }

      tags            = try(build.value.tags, [])
      images          = try(build.value.images, [])
      substitutions   = try(build.value.substitutions, {})
      queue_ttl       = try(build.value.queueTtl, null)
      logs_bucket     = try(build.value.logsBucket, null)
      timeout         = try(build.value.timeout, "600s")
    }
  }

}
