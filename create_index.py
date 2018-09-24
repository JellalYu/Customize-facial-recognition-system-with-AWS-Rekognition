import boto3

s3 = boto3.resource('s3')
rekognition = boto3.client('rekognition')

# the bucket store empolyee faces
bucket_name = '<your-bucket-name>'
bucket = s3.Bucket(bucket_name)

# A low-level client representing Amazon Simple Storage Service
client = boto3.client('s3')

# folder list
face_folders = []
# get the folder name
paginator = client.get_paginator('list_objects')
result = paginator.paginate(Bucket=bucket_name, Delimiter='/')

for prefix in result.search('CommonPrefixes'):
    # print(prefix.get('Prefix'))
    # add folder to folder list
    face_folders.append(str(prefix.get('Prefix')))
    
print(face_folders)

for folder in face_folders:
    # get all object of the folder
    objs = bucket.objects.filter(Prefix = folder)

    for obj in objs:
        # get file name
        file_name = obj.key.split('/')[1]
        # get file format
        file_format = file_name.lower().split('.')[-1]
        # print (file_format)
        
        # check fileformat
        if file_format in ['jpg','png','jpeg']:
            print (obj.key)
            
            # bulid index face in "test-mindy" collection
            index_face = rekognition.index_faces(
                CollectionId = 'mylab_collection',
                Image = {
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': obj.key,
                    }
                },
                # ExternalImageId : FirstName_LastName
                ExternalImageId = folder.replace(' ', '_').replace('/', ''),#specify an image ID
                DetectionAttributes = ['ALL',] 
            )