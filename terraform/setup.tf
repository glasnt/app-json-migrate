# Setup steps that need to be done, but may already be done. 
# Should no-op on systems that already have had a CheckboxCD deployment. 


# Cloud Run Source Deploy repo
resource "google_artifact_registry_repository" "default" {
  location      = var.region
  repository_id = "cloud-run-source-deploy"
  format        = "DOCKER"

  depends_on = [module.project_services]
}

# Cloud Build permissions
resource "google_project_iam_member" "cloud_build_roles" {
  project    = data.google_project.default.id
  depends_on = [module.project_services]
  for_each = toset([
    "roles/run.admin",
    "roles/iam.serviceAccountUser"
  ])
  role   = each.key
  member = "serviceAccount:${data.google_project.default.number}@cloudbuild.gserviceaccount.com"
}
