magentalabs/os2bos-idp-test
---------------------------
This dir and Dockerfile only exists because Gitlab CI currently Do not have a way
to either mount or copy in "dev-environment/authsources.php" to the IDP service container (needed by the frontend tests).

The image is stored on docker hub at magentalabs/os2bos-idp-test
The version string reflects the simplesamlphp version
so magentalabs/os2bos-idp-test-2.0.0 inherits from magentalabs/simplesamlphp:2.0.0.

Building image:
from the project root:
docker build -f CI/Dockerfile .

references:
https://gitlab.com/gitlab-org/gitlab-runner/-/issues/1376
https://gitlab.com/gitlab-org/gitlab-runner/-/issues/1525
