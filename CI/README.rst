magentalabs/os2bos-idp-test
---------------------------
This dir and Dockerfile only exists because gitlab ci currently dosent have a way
to either mount og copy in theauthsources.php to the idb service container needed by the fronten tests.
When this is implemented one way or the other in gitlab we.
The image is stored on docker hub at magentalabs/os2bos-idp-test
The version string reflects the simplesamlphp version
so magentalabs/os2bos-idp-test-2.0.0 inherits from magentalabs/simplesamlphp:2.0.0.

Building image:
from the project root:
docker build -f CI/Dockerfile .

references:
https://gitlab.com/gitlab-org/gitlab-runner/-/issues/1376
https://gitlab.com/gitlab-org/gitlab-runner/-/issues/1525
