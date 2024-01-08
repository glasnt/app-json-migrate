output "trigger_run" { 
    
  value = <<EOF

  Terraform apply complete. 

  To run the trigger: 

    
    gcloud builds triggers run ${google_cloudbuild_trigger.default.name} --region ${var.region} --branch ${var.github_default_branch}"  --format "value(metadata.build.logUrl)"

  Check the output log URL for deployment progress.
  EOF
}