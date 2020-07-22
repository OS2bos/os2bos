## Release X.Y.Z

## Author's checklist

- [ ] A merge request has been created for both `develop` and `master`.
- [ ] Bump the version and changelog in `NEWS.rst` and `VERSION` according to [Semantic Versioning](https://semver.org/).
- [ ] *Optional: In case of API changes, save the OpenAPI schema `openapi.yml` from `<OS2BOS URL>/api/openapi/?format=api` for use in documentation.*
- [ ] *Optional: In case of model changes, update the database model graph by running `tox -e graph` for use in documentation.*
- [ ] Test the release and verify that it doesn’t contain any breaking bugs or regressions.
- [ ] Create an `rc` tag e.g. `1.0.0-rc1` to make it deployable on Staging.
- [ ] When merged: Push `develop`, `master` and tags to the OS2BOS Github as the new core version.
- [ ] When merged: Delete the release branch