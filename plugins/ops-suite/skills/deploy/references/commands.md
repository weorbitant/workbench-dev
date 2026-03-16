# Deploy — Step-by-step Reference

This is the generic deployment process. Adapt each step using the loaded CI adapter.

## Pre-deployment checklist

1. **Verify the change is merged**
   - PR/MR must be in "merged" state
   - Note the merge commit SHA

2. **Find the build artifact**
   - Locate the CI run triggered by the merge commit
   - Verify the build completed successfully
   - Extract the image tag based on `deploy.image_tag_source`:
     - `run-id`: the CI run's database ID
     - `commit-sha`: the merge commit SHA (short or full)
     - `tag`: the git tag applied to the merge commit

3. **Review what changed**
   - List files changed in the PR
   - Check if database migrations are included
   - Check if environment variable changes are needed

## Deployment steps

4. **Confirm with user**
   - Show current vs new version
   - Show environment target
   - Get explicit confirmation

5. **Trigger deployment**
   - Use the CI adapter's deploy trigger command
   - Pass image tag and target environment

6. **Monitor**
   - Watch the deploy workflow/pipeline
   - Alert on any failures

## Post-deployment verification

7. **Verify service health**
   - Check pods/containers are running the new version
   - Verify health endpoints respond

8. **Check for errors**
   - Brief log scan for new errors in the first 2-3 minutes
   - Compare error rate to pre-deploy baseline

9. **Run migrations (if needed)**
   - If the change includes migration files, remind to run `db-migrate`
   - Always run in dev first, then prod

10. **Rollback (if needed)**
    - If errors are found, use the rollback command from the CI adapter
    - Or redeploy the previous known-good version
