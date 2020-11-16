Version 3.2.3, 2020-11-16
-------------------------

Hotfix release

Bug fixes
^^^^^^^^^

* Correctly initialize SAML in settings.py

Version 3.2.2, 2020-10-22
-------------------------

New in this version:

Bug fixes
^^^^^^^^^

- When generating payments report, catch exception if payment date is
  before case was created.


Version 3.2.1, 2020-10-13
-------------------------

New in this version:

Bug fixes
^^^^^^^^^

- Allow granting activities with no payments.
- Fix generating payments for activities that started with no payments.
- Disallow editing payments for a payment plan that is not individual.
- Update various dependencies.


Version 3.2.0, 2020-09-30
-------------------------

New in this version:

Bug fixes
^^^^^^^^^

- Don't send payment emails to internal recipients.
- Allow payments of 0 kroner.
- One time payment activities should not have main acticity end date
  set when granting.
- Proper data cleanup in GUI when user changes payment method or type.
- Allow display of Prices with no start date.
- Don't allow individual payments outside of main activity's period.
- Layout/hyphenation issue fixed.
- Date dependent price per unit must be valid at least from activity's
  start date.

Features
^^^^^^^^

- Individual payment plans.
- Stop using Postgres-specific DB field for "required fields for target
  group".
- Python packages are upgraded to include the latest security fixes.
- Warn users that future changes to SD and Cash payments will be
  overwritten.
- Allow relevant users to edit payments of type Cash and SD Løn.
- Only allow creation of new payments for individual payment plan and
  only on drafts or expectations.
- UX for Activity creation updated - user goes to the activity in read
  only mode after creating, not to the appropriation.
- Account alias and account string are shown in the same column.
- Delete button is not shown for granted payments and deleting granted
  payments is prevented by the backend.
- Appropriation PDF is updated to include individual payments.
- Audit information, responsible user and time stamp is added to rates
  and prices.
- Price history in fronted is updated to include audit fields.
- Payment per kilometer etc. are cleaned up and replaced by "running payment"
  in the database.
- Handle expectations for activities with individual payment plan.
- Update recipient on future payments when saving drafts and
  expectations.
- Backend restrictions on editing payments: Admin and workflow users
  can edit SD or Cash - other users can only mark non-paid payments (of
  the other types) as paid. Nobody can edit the amount of granted
  payments.
- CSV export files are modified to support the changes introduced in
  Phase 3.
- PRISME export will output to files, one with account alias, one
  without.
- Don't allow granting an activity with no payments.
- Don't allow user to add new payments if activity is in edit mode.


Version 3.1.1, 2020-08-31
-------------------------

New in this version:

Bug fixes
^^^^^^^^^
- Fix instance of prices being displayed with non-Danish decimal separator.
- Approximate payment calculator now uses current rate if rates are
  used.
- Enable input field validation in browser when creating activities.
- Updates list of service providers in UI based on current activity detail.
- Include global rate and price per unit information in payment email
  and PDF.


Version 3.1.0, 2020-07-09
-------------------------

New in this version:

Features
^^^^^^^^
- Add Prices and Rates.
- Add counts for draft, expected and ongoing activities.
- Don't send activity emails for one time payments.
- Prism payments account for holidays and weekends with PaymentDateExclusions.
- Main account refactoring, use new account string and remove old Account model.
- Emphasize new activities in appropriation email.
- Add pagination for Appropriation PDF.
- Add notes for Activity.
- Make Appropriation drafts deleteable.
- Display payment method when recipient is internal or company.
- Add child name, and case worker fields to activity emails.
- Set creation and modification user correctly for Case, Appropriation, Activity, RelatedPerson.
- Remove Service Providers from ActivityDetails Admin.
- Numerous styling fixes.
- Add labels to Docker files.
- Update dependencies to new versions.


Version 3.0.0, 2020-06-03
-------------------------

New in this version:

Features
^^^^^^^^

- New Django Admin user interface and permission profile for handling classifications.
- Frontend overviews have been improved.
- Account number have been refactored.
- Classifications can be marked active on/off.
- Efforts are now a classification.
- Target groups are now a classification.
- ActivityDetails now have a description.
- Related persons are now editable and can be marked 'manual' or 'from Serviceplatformen'.
- Allow hiding expired activities in the frontend.
- Improved search for payments.
- Fixed dropdown menus with only one choice.
- Frontend and Appropriation endpoint performance improvements.
- Many smaller fixes to texts.
- Update dependencies to new versions.


Version 2.6.1, 2020-04-03
-------------------------

Hotfix release

Bug fixes
^^^^^^^^^

* Use correct dates for PRISM exports for Sunday and Monday.


Version 2.6.0, 2020-03-31
-------------------------

New in this version:

Features
^^^^^^^^

- Delete payment schedules and payments when an activity is deleted.
- Send an email when an activity is expired.
- Change subject on activity deleted email.
- Change text string in frontend for closed cases.
- Add status in payments report.
- Change prism payment for Saturday, Sunday and Monday to be exported Friday.
- Add coverage and tests for management commands.
- Update dependencies to new versions.

Bug fixes
^^^^^^^^^

- Remove validation for monthly expected adjustments.


Version 2.5.0, 2020-03-06
-------------------------

New in this version:

Features
^^^^^^^^

- Add section, section_text, payment_schedule__payment_id and main_activity_name to CSV Payments report.
- Return a validation error when trying to create an invalid monthly payment schedule.
- Use create_rrule for all the places we check generated payments.
- Add tests for the frontend.
- Update README with logging documentation.
- Update documentation for generating database documentation.
- Add shell linting and docker file linting and lint fixes.
- Add automatic deployment for develop branch.
- Allow the docker backend service to be debuggable with docker attach.
- Update dependencies to new versions.


Version 2.4.2, 2020-02-24
-------------------------

Hotfix release

Bug fixes
^^^^^^^^^

* Fix fonts urlpattern for loading fonts as assets.


Version 2.4.1, 2020-02-24
-------------------------

New in this version:

Features
^^^^^^^^

* Store google fonts as assets instead of fetching them from google servers.

Bug fixes
^^^^^^^^^

* Fix duplicate payments generation.
* Remove duplicate payments in a migration.
* Add database constraint which prevents duplicate payments on date.


Version 2.4.0, 2020-01-24
-------------------------

New in this version:

Features
^^^^^^^^

* Add warning in GUI if a payment date is earlier than two days from today.
* Add restriction in GUI so an Activity can only have one expected Activity.
* Add Actual-state CSV generation for Payments.
* Improve documentation all-around.
* Change payment file default date to tomorrow.
* Update Django from 2.2.4 to 2.2.9

Bug fixes
^^^^^^^^^

* Fix CPR search for "Find sager".
* Change field 17 of PRISM file to the unique Payment pk.
* Handle missing effort steps gracefully in GUI.


Version 2.3.0, 2020-01-09
-------------------------

New in this version:

Features
^^^^^^^^

* Modify the URL for the rate tabel (taksttabel) to a more general one.
* Nice-ify django admin for Payments and PaymentSchedules and allow search on payment id.
* Add pydocstyle compliance.
* Add sphinx docs generation.

Bug fixes
^^^^^^^^^

* Fix incorrect tests dependent on current year.


Version 2.2.3, 2019-12-12
-------------------------

New in this version:

* Changes to PRISM file generation.
* Enforce rules for activities on grant.
* Disable edit for appropriation fields on granted activities.
* Enable date validation for activities.
* Add filtering on payment type.
* Fix payment CPR filtering.
* Small improvements to logging.
* Make tox work locally.
* Add frontend documentation.
* Add cronjobs for docker.
* Fix date filtering.
* Fix failing tests.
* Fix paths in settings.
* Update Django from 2.2.1 to 2.2.4


Version 2.2.2, 2019-11-28
-------------------------

Hotfix
^^^^^^

* Fix broken migration.


Version 2.2.1, 2019-11-25
-------------------------

New in this version:

Features
^^^^^^^^

* Mark payments for SD Løn along with fictive ones.

Bug fixes
^^^^^^^^^

* Fix hover text.
* Display of Indsatstrappen fixed.
* Fix ordering of Indsatstrappen.
* Recipient info stayed in GUI even though payment method was changed to
  "internal".
* Empty "not found" text when displaying "Mine sager".


Version 2.2.0, 2019-11-21
-------------------------

New in this version:

Features
^^^^^^^^

* It is now possible to find payments from a payment ID.
* Case worker can now be changed on several cases in one action.
* A log of all pending and sent emails is now kept and accessible in the
  Django admin interface.
* Payment ID and account string is displayed in the Django admin
  interface.
* Generally improved interface for searching and displaying cases.
* Fictive payments are clearly marked as fictive in payment plans.
* Fictive payments are marked as paid in the database on the day they
  are due.
* Field added in API to indicate whether a payment can be paid
  manually or not.
* Payments that are paid as Salary (through SD-Løn) or cash or are
  fictive may not be edited manually.
* Payments are paginated to avoid too long loading times.
* Payments are now sorted by payment date.
* Payments are sorted by *ascending* payment date.
* Indsatstrappen is now a classification to be maintained in the Django
  Admin interface.
* Section (of the law, from the appropriation) is added to the payment
  emails.
* Emails are sent for all approved payments, for all combinations of
  payment and recipient types.
* Complex logic for generation of account string.
* Payment dialog improved.
* Integration to KMD PRISME accounting system.
* Information about citizen included in display of appropriation.


Bug fixes
^^^^^^^^^

* Don't throw an exception if users attempt to access the API without
  logging in, just deny access.
* If more than one user profile is sent from SAML IdP, don't crash -
  choose the *highest* one.
* "Mixed content error" on some pages (on internal test server).
* Many small and big improvements to styling and usability.
* Function deciding if case is expired also looked at DELETED
  activities.


Version 2.0.1, 2019-11-11
-------------------------

New in this version:

* Add support for Service Provider certificates through PySaml2.


Version 2.0.0, 2019-11-06
-------------------------

New in this version:

* Implement SAML SSO login.
* Implement user rights levels.
* Add preliminary Prism file generation.
* Implement GUI for editing payments.
* Add support for "fictive" payments.
* Add support for negative and zero payments.
* Add support for paid amounts and paid date for payments.
* Update payment summation to include paid amounts when able.
* Add new payment ID for payment plans.
* Add account strings for payments.
* Add API filtering for several endpoints.
* Remove the "udbetaling til firma" payment option.
* Fix a bug when creating an activity.
* Fix redirect when setting a payment paid.
* Add missing verbose names in Django admin.


Version 1.1.1, 2019-10-30
-------------------------

Hotfix release.

New in this version:

* Deleted main activity no longer blocks for creating a new main activity.
* Granted activities are now explicitly included in the appropration PDF.
* Fix activities still being checked for granting when closing the grant dialog.
* Fix not being able to grant an expected main activity.
* Fix invalid XML in OS2forms.xml.
* Add missing constraint for creating supplementary activities based on allowed main activities.


Version 1.1.0, 2019-10-04
-------------------------

New in this version:

* Fixed approval button when there's nothing to approve.
* Fixed missing activities from appropriation PDF.
* Fix spelling error in logout message.
* For payment to a person with SDLøn, tax card is mandatory.
* Use user first_name and last_name instead of initials for Sagsbehandler dropdown.
* Fix stop dates on supplementary activities.
* Fix link to rates document.
* Correctly calculate the expected amount for expected activities.
* Correct forms for modifying effort steps (Indsatstrappe) in Djang Admin.
* Clear frontend errors correctly.
* Rearrange autologin scripts in frontend.
* Change recommended browser text.
* Suppress not writeable warning from ipython.


Version 1.0.0, 2019-09-27
-------------------------

First production release. New in this version:

* KLE number and SBYS template info moved from Section to new
  SectionInfo class in the ManyToMany relation.
* Activities are granted individually, not all at once for each
  appropriation.
* Missing logo fixed/supplied.
* Various GUI and UX improvements.
* Prevent expected changes from starting in the past.
* Make user supply day of month for monthly payments - handle month end
  correctly.
* Browser compatibility fixes.
* Fix missing update of family relations.
* Improved handling of backend error messages.
* New API fields for expected and granted totals for activities.
* Appropriation PDF nicified and adapted to the new approval scheme.
* SBSYS integration (os2forms.xml) fixed.
* Cases *must* have a team, this field is now non-nullable.
* Activities with status EXPECTED are now soft-deleted.
* Status label for appropriations fixed.
* Wrong validation of KLE numbers fixed.
* Stop date of supplementary activities must be no later than stop date
  of main activity.
* End-to-end tests for accessibility added.
* Classifications updated, now production ready.
* Bad validation that expectation must be after next payment date
  removed.
* Allow units to be charged, e.g. dates, to be a decimal number.
* Gunicorn is now run single-threaded.
* Updates to Docker configuration.
* It is now possible to make expectations for the entire appropriation
  period even though the main activity is split.
* DB representation of effort steps (Indsatstrappe) changed to integer.


Version 0.5.0, 2019-09-05
-------------------------

New in this version:

* initial release
