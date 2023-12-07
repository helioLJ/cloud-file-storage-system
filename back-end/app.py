import json
from flask import Flask, jsonify, make_response, request, send_file
import boto3
from flask_cors import CORS  # Importe a extensão CORS

# Configuração do cliente S3 para o LocalStack
s3 = boto3.client('s3', endpoint_url='http://localhost:4566')

# Nome do bucket
bucket_name = 'meuprojeto-localstack-bucket'

# Verifica se o bucket existe, e cria se não existir
existing_buckets = s3.list_buckets()['Buckets']
if not any(bucket['Name'] == bucket_name for bucket in existing_buckets):
    s3.create_bucket(Bucket=bucket_name)

# Configuração do cliente DynamoDB
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566')

# Nome da tabela no DynamoDB para armazenar metadados
metadata_table_name = 'file_metadata'

# Verifica se a tabela existe, e cria se não existir
existing_tables = dynamodb.tables.all()
if metadata_table_name not in [table.name for table in existing_tables]:
    metadata_table = dynamodb.create_table(
        TableName=metadata_table_name,
        KeySchema=[
            {'AttributeName': 'file_key', 'KeyType': 'HASH'}  # Chave primária
        ],
        AttributeDefinitions=[
            {'AttributeName': 'file_key', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    metadata_table.wait_until_exists()

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400
    
    file = request.files['file']
    file_key = file.filename

    # Upload do arquivo para o S3
    s3.upload_fileobj(file, bucket_name, file_key)

    # Armazenar metadados no DynamoDB
    metadata_table = dynamodb.Table(metadata_table_name)
    metadata_table.put_item(Item={'file_key': file_key, 'filename': file_key})

    # Acionar a função Lambda após o upload
    lambda_client = boto3.client('lambda', endpoint_url='http://localhost:4566')  
    response = lambda_client.invoke(
        FunctionName='print-lambda',
        InvocationType='RequestResponse',  
        # InvocationType='Event',  
        Payload=json.dumps({'filename': file.filename})
    )

    try:
        # Read the content of the StreamingBody
        payload_content = response['Payload'].read()
        print(payload_content)

        # Attempt to decode the response payload
        response_body = json.loads(payload_content.decode('utf-8'))

        # Returning the response from Lambda
        return jsonify({
            'message': 'Upload bem-sucedido e função lambda executada',
            'lambda_response': response_body
        }), 200
    except json.JSONDecodeError as e:
        # Handle JSON decoding error
        return jsonify({
            'message': 'Erro ao processar a resposta do Lambda',
            'error': str(e),
            'raw_payload': payload_content.decode('utf-8')
        }), 500

@app.route('/list_files', methods=['GET'])
def list_files():
    # Lista os objetos no S3
    s3_objects = s3.list_objects(Bucket=bucket_name)['Contents']
    
    # Recupera os metadados do DynamoDB
    metadata_table = dynamodb.Table(metadata_table_name)
    file_metadata = {item['file_key']: item for item in metadata_table.scan()['Items']}

    # Combina informações do S3 e do DynamoDB
    file_list = [{'filename': obj['Key'], 'metadata': file_metadata.get(obj['Key'], {})}
                 for obj in s3_objects]

    # Cria uma lista de links de download
    download_links = [{'filename': file_info['filename'], 'download_link': f"/download/{file_info['filename']}"} 
                      for file_info in file_list]

    return jsonify(download_links)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Recupera o arquivo do S3
    s3_response = s3.get_object(Bucket=bucket_name, Key=filename)
    file_content = s3_response['Body'].read()

    # Cria uma resposta Flask e a envia como um anexo para download
    response = make_response(file_content)
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@app.route('/delete_file/<filename>', methods=['DELETE'])
def delete_file(filename):
    # Excluir o arquivo do S3
    s3.delete_object(Bucket=bucket_name, Key=filename)

    # Excluir metadados do DynamoDB
    metadata_table = dynamodb.Table(metadata_table_name)
    metadata_table.delete_item(Key={'file_key': filename})

    return 'Arquivo excluído com sucesso', 200

if __name__ == '__main__':
    app.run(debug=True)
