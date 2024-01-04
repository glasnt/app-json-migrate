#https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github#connecting_a_github_host_programmatically


# Google Cloud Services to enable
module "project_services" {
  source                      = "terraform-google-modules/project-factory/google//modules/project_services"
  version                     = "14.4.0"
  disable_services_on_destroy = false

  project_id                  = data.google_project.project.project_id
  activate_apis = [
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com",
  ]
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

variable "github_token" {
  # Generate at https://github.com/settings/tokens/new
  description = "GitHub token with repo and read:user permissions"
}


data "google_project" "project" {}

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
  member = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
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
  name = "my-trigger-2"
  location = "us-central1"

  repository_event_config {
    repository = google_cloudbuildv2_repository.default.id
    push {
      branch = "^main$"
    }
  }

  #filename = "cloudbuild.yaml"

  build {
    step {
      name = "ubuntu"
      args = ["echo", "hello there"]
    }
  }
}
