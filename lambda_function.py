import os
import boto3
import json
import re
import logging


def lambda_handler(event, context):

	rekognition = boto3.client('rekognition')
	sns = boto3.client('sns')
	s3 = boto3.resource('s3')
	rekognition_collection_id = "mylab_collection"
	face_match_threshold = 60

	print ("=================Lambda Start=================")
	print (event)
	bucket_name = event['Records'][0]#['s3']['bucket']['name']
	object_name = event['Records'][0]#['s3']['Object']['key']
	dict_event = event['Records'][0]
	
	s_object_name = dict_event['s3']['object']['key']
	print (s_object_name)

	print(bucket_name)
	print(object_name)
	print(s_object_name)
	
	resource_bucket_name = '<your bucket name>'
	aim_bucket_name = '<your bucket name>'

	print ("Bucket: " + resource_bucket_name)
	print ("Object: " + s_object_name)
    
	pattern = re.compile('.jpg$|.png$|.jpeg$|.JPG$|.PNG$|.JPEG$')
	if pattern.findall(s_object_name):
	    print ("It's vaild input: " + pattern.findall(s_object_name)[0])
	else:
	    print ("Sorry, not supported format")
	    return 0
    
	rekognition_response = rekognition.search_faces_by_image(
		CollectionId = rekognition_collection_id,
		Image = {
			'S3Object': {
				'Bucket': resource_bucket_name,
				'Name': s_object_name
			}
		},
		MaxFaces=123,
		FaceMatchThreshold = face_match_threshold
	)
	
	print (rekognition_response)
	print ("=================Rekognition Response=================")
	print (json.dumps(rekognition_response, indent = 4))
	
	print ("=================Face Match Result====================")
	face_matches = rekognition_response['FaceMatches']
	print (face_matches)
	
	face_matches_result_id = rekognition_response
	print (face_matches_result_id)
	
	if len(face_matches) > 0:
	    print ("match!")
	    print ("=================Item=================")
	    face_matches_result_id = rekognition_response['FaceMatches'][0]['Face']['ExternalImageId']
	    print (face_matches_result_id)
	    face_matches_result_id = []
	    for item in rekognition_response['FaceMatches']:
	        print (item)
	        face_matches_result_id.append(item['Face']['ExternalImageId'])
	        
	    print (face_matches_result_id)
	    print (set(face_matches_result_id))
	    print ("=================Moving Picture=================")
	    for face_id in set(face_matches_result_id):
	        print (face_id)
	        aim_object_name = ('rekognition-result' + '/' + face_id + '/' + s_object_name)
	        s3.Object(aim_bucket_name, aim_object_name).copy_from(CopySource={'Bucket': resource_bucket_name, 'Key': s_object_name})
	        print ("Moving to %s" % (aim_bucket_name + aim_object_name))
	    
	    s3.Object(resource_bucket_name, s_object_name).delete()
	    sns.publish(TopicArn ='<your SNS ARN>', Subject = 'Recog_result: ', Message = 'match'+ face_id)

	    
	else:
	    print ("looks like someone else.")
	    aim_object_name = ('rekognition-result' + '/not-found/' + s_object_name)
	    s3.Object(aim_bucket_name, aim_object_name).copy_from(CopySource={'Bucket': resource_bucket_name, 'Key': s_object_name})
	    s3.Object(resource_bucket_name, s_object_name).delete()
	    sns.publish(TopicArn = '<your SNS ARN>', Subject = 'Recog_result: ', Message = 'Someone else publish a different photo')
