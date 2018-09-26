## Scenario    
Deep learning has been quietly applied to our daily lives, and image recognition is a good example. If users have the need of face recognition in practical applications, a simple way is to use Amazon Rekognition services to build their own database. For example, this technology could be used for corporate employee access or check-in systems by utilizing Amazon Rekognition API to build an application architecture based on AWS serverless service.

This lab uses the face images of Creative Commons (CC) to create user's own collection indexes. When the image import into the S3 database, it can trigger lambda to send back the face recognition result to the user through Amazon SNS.


![1.png](/img/1.png)


## Lab Tutorial

### Create Cloud9 IDE Environment

1. In AWS console, open Cloud9.
2. In your environments page, click **Create environment**.
3. In name environment page, type your own cloud9 environment name and description then click **Next step**.
![2.png](/img/2.png)
4. In Configure settings page, keep all the setting default and click **Next step**.
5. Review the settings and click **Create environment**.

### Create S3 bucket
This part we use AWS CLI to build a bucket directly, which is used to place the faces pictures and trigger lambda events.

1.    Open your cloud9 IDE and paste the following code in the console to install AWS CLI and set python environment:
```
#Install CLI
sudo yum -y update 
sudo yum -y install aws-cli
#Install python
curl -O https://bootstrap.pypa.io/get-pip.py 
sudo python get-pip.py
rm get-pip.py
sudo python -m pip install boto3
```

like this:

![3.png](/img/3.png)



2.    Type the following script to build an S3 bucket in N.Virginia region. 
> Note that the bucket name here is unique.
```
aws s3 mb s3://<your-own-bucket> --region us-east-1
```

3.    Go to S3 service page. Put the sub-folders of **DataFace** from this GitHub into your S3 bucket.

![4.png](/img/4.png)

### Create collection and index
This step is to create your own collection, which will be used to place the index of each face. The index is the feature of the image.

1.    Type the following script into the Cloud9 environment. This is for creating Amazon Rekognition collection in N.Virginia region.

```
aws rekognition create-collection --collection-id mylab_collection --region us-east-1 
```

2.    Create indexes

Paste the following python script into Cloud9 **New file** and save the name as “create_index.py”.
```
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
```


### Integrate with serverless application
1. On the Services menu, click **Lambda**.
2. Click **Create function**.
3. Choose **Author from scratch**.
4. Enter function Name **rek_lambda**.
5. Select **python 3.6** in Runtime blank.
6. Select **Choose an existing role** in **Role** blank and choose **myRek_role** as Existing role. If the role is not existing, choose **create a new role**.
7. If you don’t have the role, click the role name as **myRek_role** and paste the following code in policy document:

![5.png](/img/5.png)

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::bucket-name/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "rekognition:IndexFaces"
            ],
            "Resource": "*"
        }
    ]
}
```
8. Click **Allow**.
9. Go back to rek_lambda function setting page, from **Designer** section choose and drag S3 into **trigger list from the list on the left** column.

![6.png](/img/6.png)

10. Paste the python script in this GitHub repository to **Function code**. You should change the S3 bucket name and SNS ARN before you test.

![7.png](/img/7.png)

11. In **Basic settings** set **Timeout** to 5 min.

![8.png](/img/8.png)

12. Click **Save**.

### Set SNS notification
1.    In AWS console, choose SNS (Simple Notification Service).
2.    Click **Topics** at left navigation bar and click **Create new topic**.
3.    Type your topic name and display name, then click **Create topic**.
4.    Click into your SNS and create the subscription with your own email.

![9.png](/img/9.png)

5.    Copy the ARN of SNS notification you just created and paste to your lambda function.

![10.png](/img/10.png)

### Test solution architecture
1.    Go to google.com find the image like the face image you put into S3 bucket.
2.    Check you can get the recognition result notification by email from Amazon SNS.

## Clean Up
After this tutorial, you should remove some resource to save account cost.
* Cloud9 environment
* Lambda function
* S3 bucket

## Conclusion
* Congratulations, through this Lab you can now: 
1. Create your own Rekognition collection with specific faces index.
2. Use serverless to make an event trigger S3 and Rekognition applications.
3. Use cloud9 to build service environment.


## Reference
* [**Build Your Own Face Recognition Service Using Amazon Rekognition**](https://aws.amazon.com/tw/blogs/machine-learning/build-your-own-face-recognition-service-using-amazon-rekognition/)

