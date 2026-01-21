from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType, TimestampType
from pyspark.sql.functions import col, to_timestamp
import psycopg2

# Configurações Spark
spark = SparkSession.builder.appName('ThingSpeakToPostgres').getOrCreate()

# Esquema dos dados recebidos
schema = StructType([
    StructField('created_at', StringType(), True),
    StructField('entry_id', IntegerType(), True),
    StructField('field1', StringType(), True),
    StructField('field2', StringType(), True),
    StructField('field3', StringType(), True),
    StructField('field4', StringType(), True)
])

# Configuração do PostgreSQL
pg_config = {
    "url": "jdbc:postgresql://localhost:5432/sistema_irrigacao",
    "driver": "org.postgresql.Driver",
    "user": "",
    "password": ""
}

# Função para criar a tabela no PostgreSQL se não existir
def create_table():
    conn = psycopg2.connect(
        dbname='sistema_irrigacao',
        user=pg_config['user'],
        password=pg_config['password'],
        host='localhost'
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dados_sistema_irrigacao (
            created_at TIMESTAMP,
            entry_id INT,
            field1 FLOAT,
            field2 FLOAT,
            field3 FLOAT,
            field4 VARCHAR(50)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Criar a tabela antes de salvar os dados
create_table()

# Função para gravar dados no PostgreSQL
def save_to_postgres(df, epoch_id):
    df.write \
        .format("jdbc") \
        .option("url", pg_config["url"]) \
        .option("dbtable", "dados_sistema_irrigacao") \
        .option("user", pg_config["user"]) \
        .option("password", pg_config["password"]) \
        .option("driver", pg_config["driver"]) \
        .mode("append") \
        .save()

# Leitura do arquivo JSON com Spark
json_df = spark.read.json("data.json", schema=schema)

# Convertendo os tipos de dados
json_df = json_df.withColumn("field1", col("field1").cast(FloatType()))
json_df = json_df.withColumn("field2", col("field2").cast(FloatType()))
json_df = json_df.withColumn("field3", col("field3").cast(FloatType()))
json_df = json_df.withColumn("created_at", to_timestamp(col("created_at"), "yyyy-MM-dd'T'HH:mm:ss'Z'"))



# Verificar dados lidos para garantir que estão corretos
print("Dados após a leitura e conversão:")
json_df.show(truncate=False)

# Verificar esquema do DataFrame
print("Esquema do DataFrame após a conversão:")
json_df.printSchema()

# Processar e salvar dados no PostgreSQL
save_to_postgres(json_df, None)
