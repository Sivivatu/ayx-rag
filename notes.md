# 2025-11-10
1. when running `uv run main.py sitemap-filter alteryx-help-current-sitemap.xml --language en --product server -f json --output downloads/urls/sitemap-filtered-server.json` the process fails if the folder doesn't exist. Need to update the command to check file exists and give option to create
2. usage description for the page-downloader (in the help menu) only references the url. this needs to be updated to reflect the url/file use
3. format of the json file isn't recognised by the page downloader as it expects only a list of urls not the formatted schema that the json output provides. 
4. should i make the cert check a warning rather than error?
5. need to reorder the readme quickstart to reflect the proper order of sitemap download -> filter -> page download -> html convert
