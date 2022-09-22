# Python Template
* Internal template to start the process of making a new application in the model/service format.
* This repo should NOT be modified except when undergoing improvements. If a new application is being made, a new repo should be made that uses this repo as its template.
## Getting Started
* Read [Python best practices page](https://aoms-tech.atlassian.net/wiki/spaces/HWI/pages/2006188061/Python+Best+Practices)
## Directories
### <span style="color: LightCoral"> Directory: python_template </span>
* This is the directory that houses the application.
* This directory name should automatically change when a new repo is made off of this template. This directory name will match the repo name.
#### <span style="color: CadetBlue"> File: main.py </span>
* There are a few lines that **MUST** be modified, everything else should not be modified.
* <span style="color: GoldenRod"> TODO: Modify lines that are surrounded by the following comment convention: </span>
```
# todo: <instructions>
<CODE MODIFICATION>
# end todo
```
#### <span style="color: CadetBlue"> File: settings_python_template.yaml </span>
* An example of how a yaml file should look. All .yaml files unique to the application should be located in this directory.
* It is best practice to make all .yaml files follow this naming convention: `settings_<name>.yaml`
* <span style="color: GoldenRod"> TODO: Add .yaml files to this directory. </span>
### <span style="color: LightCoral"> Directory: config </span>
* This is a default directory and no files should be added here.
#### <span style="color: CadetBlue"> File: settings_config.yaml </span>
* Only has one setting: SettingsFiles. 
  * This is a list of .yaml files that the model configuration is built on. 
  * This means that settings can be split into multiple .yaml files. For example, you may want a settings_public.yaml that users can edit, and a settings_private.yaml that users can't edit. 
  * <span style="color: GoldenRod"> TODO: Append .yaml file names to the SettingsFiles list.
#### <span style="color: CadetBlue"> File: settings_logging.yaml </span>
* This file holds the settings for the logger. 
* <span style="color: GoldenRod"> TODO: Modify this file if you want a different logging configuration. </span>
### <span style="color: LightCoral"> Directory: lib/external </span>
* This is where any submodules from github would go. For example, pythontools is inserted here.
* The links to the necessary submodules are included here.
* <span style="color: GoldenRod"> TODO: Add the links in this folder as submodules to your application's repo. If your application has no repo, simply clone these links into this folder, then. </span>
### <span style="color: LightCoral"> Directory: lib/internal/model </span>
* this is where python scripts that hold models are located.
> **_Model_**
> 
> Definition: Objects that have properties, but no functions.
> 
> File Naming Convention: "<application\>.py"
#### <span style="color: CadetBlue"> File: python_template.py </span>
* <span style="color: GoldenRod"> TODO: Change the name to match your application. </span>
* <span style="color: GoldenRod"> TODO: Follow the todo comments in code. </span> 
### <span style="color: LightCoral"> Directory: lib/internal/service </span>
* This is where python scripts that hold services are located.
> **_Service_**
> 
> Definition: Functions that have models as a parameter. The function specifically modifies or utilizes the model properties.
> 
> File Naming Convention: "<application\>_service.py"
#### <span style="color: CadetBlue"> File: python_template_service.py </span>
* <span style="color: GoldenRod"> TODO: Change the name to match your application. </span>
* <span style="color: GoldenRod"> TODO: Follow the todo comments in code. </span> 
### <span style="color: LightCoral"> Directory: lib/internal/unittest </span>
* This is where python scripts that hold unittests are located.
> **_Unittest_**
> 
> Definition: A unittest class that contains functions intended to test service functions.
> 
> File Naming Convention: "<application\>_unittest.py"
#### <span style="color: CadetBlue"> File: python_template_service.py </span>
* <span style="color: GoldenRod"> TODO: Change the name to match your application. </span>
* <span style="color: GoldenRod"> TODO: Follow the todo comments in code. </span> 
