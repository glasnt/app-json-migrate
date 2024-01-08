
variable "github_repo" {
  description = "Name of your github repo"
}

variable "region" {
  default = "us-central1"
}

variable "cloudbuild_file" { 
  default = "cloudbuild.yaml"
}

variable "installation_id" {
  # Find from Cloud Build listing on https://github.com/settings/installations 
  description = "ID of the github installation. https://github.com/settings/installations/INSTALLATION_ID"
}

variable "github_token" {
  # Generate at https://github.com/settings/tokens/new
  description = "GitHub token with repo and read:user permissions"
}

variable "github_default_branch" { 
  default = "main"
  description = "branch of repo to attach to"
}
