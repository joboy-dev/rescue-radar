import json, re
from uuid import uuid4


with open('api/core/dependencies/articles.json', 'r') as f:
    resources = json.load(f)
    
for resource in resources:
    resource['url_slug'] =  re.sub('[^a-zA-Z0-9 \n]', '', resource['title']).lower().replace(' ', '-')
    resource['id'] = uuid4().hex

# Save changes to file
with open('api/core/dependencies/articles.json', 'w') as f:
    json.dump(resources, f, indent=4)
