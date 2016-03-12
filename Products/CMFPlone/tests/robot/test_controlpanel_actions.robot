*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: Modify an existing action in Actions Control Panel
  Given a logged-in administrator
    and the actions control panel
   When I modify an action title
   Then anonymous users can see the new action title

Scenario: Reorder in Actions Control Panel
  Given a logged-in administrator
    and the actions control panel
   When I change the actions order
   Then anonymous users can see the actions new ordering

Scenario: Create a new action in Actions Control Panel
  Given a logged-in administrator
    and the actions control panel
   When I add a new action
   Then logged-in users can see the new action

Scenario: Delete an action in Actions Control Panel
  Given a logged-in administrator
    and the actions control panel
   When I delete an action
   Then anonymous users cannot see the action anymore

*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in administrator
  Enable autologin as   Manager

the actions control panel
  Go to  ${PLONE_URL}/@@actions-controlpanel

# --- WHEN -------------------------------------------------------------------

I modify an action title
  Click Link    css=section:nth-child(3) li:first-child a
  Wait until page contains  Action Settings
  Input Text for sure  form.widgets.title  A new site map
  Click Element  css=.pattern-modal-buttons > input

I change the actions order
  Click Link    css=section:nth-child(3) li:first-child a
  Wait until page contains  Action Settings
  Input Text for sure  form.widgets.position  3
  Click Element  css=.pattern-modal-buttons > input

I add a new action
  Click Link  Add new action
  Wait until page contains  New action
  Select From List By Label   form.widgets.category:list   User actions
  Input Text for sure  form.widgets.id  favorites
  Click Element  css=.pattern-modal-buttons > input
  Wait until page contains  favorites
  Click Link    css=section:nth-child(7) li:last-child a
  Wait until page contains  Action Settings
  Input Text for sure  form.widgets.title  My favorites
  Input Text for sure  form.widgets.url_expr  string:\${globals_view/navigationRootUrl}/favorites
  Click Element  css=.pattern-modal-buttons > input

I delete an action
  Click Button    css=section:nth-child(3) li:first-child input[type=submit]
  Confirm Action

# --- THEN -------------------------------------------------------------------

anonymous users can see the new action title
  Disable autologin
  Go to  ${PLONE_URL}
  Page Should Contain  A new site map

anonymous users can see the actions new ordering
  Disable autologin
  Go to  ${PLONE_URL}
  Page Should Contain Element   xpath=//footer[@role='contentinfo']//aside//ul/li[1]/a/span[contains(text(), 'Accessibility')]
  Page Should Contain Element   xpath=//footer[@role='contentinfo']//aside//ul/li[3]/a/span[contains(text(), 'Site Map')]

logged-in users can see the new action
  Disable autologin
  Enable autologin as   Contributor
  Go to  ${PLONE_URL}
  Page Should Contain  My favorites

anonymous users cannot see the action anymore
  Disable autologin
  Go to  ${PLONE_URL}
  Page Should Not Contain  Site map