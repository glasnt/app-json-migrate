# `app.json` migrate (ajm)

This is a proof of concept application that migrates a Cloud Run Button `app.json` into a `cloudbuild.yaml`. 


## Known limitations

 * `env`: 
    - Any declared `env` values are populated as substitution variables, and assigned to the Cloud Run service as environment variables.
    - `descriptions` are added as comments (TODO but lost in validation)
    - `order` is ignored. 


 * `generated` environment variables
    - Not yet implemented
    - Generating the value into the cloudbuild.yaml would result in plaintext passwords. 
    - Could create a secret and generate a value there, but would require Cloud Build to have Secret Manager permissions. 


   * 
   * `env.ORDERED_ENV`
     * Cloud Build offers no ability to prompt, so ordered prompts can't be supported. 
   * 