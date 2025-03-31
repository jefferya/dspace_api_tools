# Subset of Jupiter content via a Ruby irb script to output the metadata in CSV format
# Usage: irb -r ./juptiter_collection_metadata_to_CSV.rb

ITEM_SUBSET = [
'0e790a8e-a263-4a99-9a77-418d91b700c0',                                         
'204c4969-4b26-4737-9482-39981fca2ded',
'285a73a4-fa9d-41f8-9df3-c92956a338cd',
'297d92b8-f255-49ff-9835-b52c7c1a0b6a',
'2c5219bd-01e4-4b1b-8c9f-2c3bddf12c0e',
'2e7f1207-79dd-4620-9a01-127f66c81def',
'2f3407d5-193a-4a9e-b2cb-633ffd7c8a3f',
#'3424cccc-3bfb-4ba1-992e-37c5adfd52bf', not found in prd
'369dad5d-f221-4973-92aa-e9ce673cd58f',
'3d6b31c2-686c-4c62-a598-eda1cf159125',
'5a0aad85-bffa-4686-bae3-d589a64361dc',
'69c8b80b-2251-4ed3-9fd4-5f433c30e521',
'8d2ccf90-1cec-474b-9d83-b6d7bc02704c',
'90fb3051-2a0f-4217-89a4-fc0ce2bfd672',
'930915e9-aad9-46e6-9b98-72c379789869',
'a20df6be-4fc3-4a19-aeea-6609474bec3f',
'b464a3dc-510d-4625-a009-75dddaac1c91',
'be7d39d9-9561-4485-a6f2-0f69f8084f83',
# 'c3bcf748-5676-4b58-bdbe-168590b0bbbc', not found in prd
'c8d55e58-b23f-421c-a75a-7c26c67a1c48',
'c97c1a89-c2aa-49ae-9c26-d7560d8dfdc0',
'c9f40f8c-56d1-4acd-80d6-dca64bd3e068',
'cc9de8a2-ec54-46e2-b1a3-f3e34e7c762c',
'd0973c15-8cff-431c-94e5-c21738e09594',
'd18f9dd3-afda-4108-b32c-fff2ccbf93cf',
'd3a154a1-cdb5-4a27-8074-c598448ea5df',
'd8ab19e4-1f58-404d-a7f1-e7ac071d0a74',
'db0339cf-5faf-4f28-9a25-5360bad5e8d9',
'dd5e240c-533e-482c-9141-fcbab6362d50',
'e22bb1bc-cdc5-4cc7-b907-8cc723599ec2',
'f3678283-1807-4016-90e4-07f5dde4efd3'
].freeze

THESIS_SUBSET = [
'b5815a02-dd7f-4c9a-a69b-717e0c80e432',
'b1e7fec6-80f8-448f-a9a1-05eeb180eff9',
'0c22e6da-f19f-45d4-a487-9c9faa7423db',
'0412e7d4-63f2-4deb-80ba-d1088d46c522',
'49442413-75c8-400c-905a-ac93084893b9',
'9001b1c8-74ae-4973-a6a0-ba6b3197b57d',
'c85ec3eb-8cea-4b1a-b6cc-c88fa22289ba',
'64d9b5e6-45cf-4d89-bbb4-09315b90165a',
'a9ea310f-ca87-4529-9471-6110a323f9b3',
'e50e8980-fa0a-498d-878d-5818fe57c6c5',
'33e04d11-53bb-495c-a90d-d7a43391ebd4',
'17dddffb-862e-4cd0-a924-e860cc3879a2',
'2462ebf1-bc8d-4a27-b16e-323631a5dfea',
'513af89a-0bd5-490c-9f58-4cb7d2dda91b',
'28d9417a-4f55-4992-b5a3-b8aa1b1d6794',
'0ff180ab-8a0e-41ce-bd0e-d01d02b8560c',
'f977690e-403a-4705-9057-c88fde4efd42',
'9e0abecd-4517-4db6-9634-a38c61c01390',
'cf64445a-fcd9-4a62-b462-5e71840c0f08',
'7b0a5712-9dda-4c8c-80a9-116038848a79',
'8e3f17b3-f580-497a-893e-73c921112d61',
'90f4c222-e1f6-4207-87f9-10fc5c771d1f',
'7e6495ba-099c-45a0-b323-333ff694dcd3',
'9ba70cda-217c-491a-a959-035067dd5f04',
'6e23f6dc-8bb3-4f8e-a2f9-e5286cc57525',
'0584ddf8-7455-4d2f-9ce7-6775cd773e97',
'fbfc3d80-7ec0-4cc3-b637-0b45d3d27782',
'749fe821-fe78-4390-a386-994e2f100255',
'b0fcb068-14f1-4eae-98b2-15e19e906e2e',
'9fef8dfd-abb0-4285-85cc-d5782be336d7',
'865f666a-b097-4cd2-b92e-6eedb4383d8a',
'8248a68a-6fb0-4b77-b9b4-29c004400cb1',
'1bbc990a-d92e-41e0-83d0-c5725ff36f7d',
'165cb3c5-5473-4094-945f-e536c5d11b2b',
'bfd72ccc-b050-4f18-9d4a-c90d68df5a72',
'492ba2d6-9fc9-4d61-a66a-9c1db4244de7',
'b5357307-5c61-46a5-a28f-9291fba04a2d',
'079283f4-3644-4320-8151-a4ffedd2b7c9',
'87912c01-ceab-4c0b-8a97-e3326ce11b56',
'5ef01c36-f1e1-4130-9d9d-399be3abdef6',
'871b07c9-fbac-480e-84a7-bcd972605ac3',
'fa5aad6d-c5c6-472c-8bdf-8f1c2932ab74',
'84afc1dc-91bb-4f28-9dc0-1da36ba1ae04',
'3b31a9f2-2f47-448c-a60f-b04dbf71907c',
'7c300bd0-a4c5-4562-bcb1-a7643e5abfa6',
'773d9696-8d70-43a1-888d-d2b18edff78f',
'612a5863-60c2-4982-be21-c8f59539084b',
'a9cc825f-f974-4284-ad06-7f81159fa450',
'af31d209-52f4-4e3f-b481-7129e8db3c7d',
'3975ecea-e51f-4897-9962-c71d9663dad8',
'892743c8-8d9a-4fe2-996c-17504f751509',
'dde1c8ae-c9ef-411f-a8e3-c411f37ab5ea',
'fc83bb92-bbc6-4cce-9a81-b55f00ad3285',
'235bc78a-f825-4162-8ab6-489a6c37c833',
'e4ee653c-21ab-4a18-9802-bd1e1e6488c8',
'907ac2b1-93a5-4575-bcef-3f65440a7588',
'553cda41-a3fa-4c6a-a969-f21845297d38',
'dd1038a1-95de-4ae6-905d-dd0c2c8d7d3f'
].freeze

#ITEM_SUBSET = [
  #"047630f2-beba-4895-b7da-78c1a0219a92"
#].freeze

class JupiterBasicMetadataToCSV
  def initialize()
    @output_file = ""
    @instance = nil
  end
  def enumerable
    @instance.find_each() do |i|
      yeild i
    end
  end
  def run
    raise "Instance not set" unless @instance
    headers = @instance.new.decorate.attributes.keys
    CSV.open(@output_file, 'wb', write_headers: true, headers: headers) do |csv|
      enumerable do |i|
        csv << i.decorate.attributes.values
      end
    end
  end
end

# Jupiter Item metadata 
class JupiterItemMetadataToCSV < JupiterBasicMetadataToCSV
  def initialize(output_directory)
    super()
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "jupiter_item_#{@date_time}.csv"
    @instance = Item 
  end
end

# Subset of Jupiter Item metadata 
class JupiterItemMetadataToCSVSubset < JupiterBasicMetadataToCSV
  def initialize(output_directory)
    super()
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "jupiter_item_subset_#{@date_time}.csv"
    @instance = Item 
  end
  def enumerable
    ITEM_SUBSET.each do |i|
      yield @instance.find(i)
    end
  end
end

# Subset of Jupiter Thesis metadata 
class JupiterThesisMetadataToCSVSubset < JupiterBasicMetadataToCSV
  def initialize(output_directory)
    super()
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "jupiter_thesis_subset_#{@date_time}.csv"
    @instance = Thesis 
  end
  def enumerable
    THESIS_SUBSET.each do |i|
      yield @instance.find(i)
    end
  end
end


# Juptier Active Storage Blob and Item metadata
class JupiterItemActiveStorageBlobMetadataToCSV
  def initialize(output_directory)
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "jupiter_item_activestorage_#{@date_time}.csv"
    @instance = Item
  end
  def enumerable
    @instance.find_each() do |i|
      yeild i
    end
  end
  def run
    # "provenance.ual.jupiterId.item" & "bitstream.sequenceId" labels need to align
    # with the DSpace CSV for use with pandas dataframe multi-index join
    # in the comparison script 
    headers = ["item.id",
                "item.title",
                "provenance.ual.jupiterId.item",
                "bitstream.sequenceId",
                "key",
                "filename",
                "content_type",
                "metadata",
                "byte_size",
                "checksum",
                "created_at"] 
    CSV.open(@output_file, 'wb', write_headers: true, headers: headers) do |csv|
      enumerable do |item|
        sequence_num = 0
        item.ordered_files.each do |f|
          sequence_num += 1
          csv << [item.id,
                  item.title,
                  item.id,
                  sequence_num,
                  f.blob.key,
                  f.blob.filename,
                  f.blob.content_type,
                  f.blob.metadata,
                  f.blob.byte_size,
                  f.blob.checksum,
                  f.blob.created_at]
        end
      end
    end
  end
end

# Subset of Juptier Active Storage Blob and Thesis metadata
class JupiterItemActiveStorageBlobMetadataToCSVSubset < JupiterItemActiveStorageBlobMetadataToCSV 
  def initialize(output_directory)
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @instance = Thesis 
    @output_file = output_directory + "jupiter_thesis_activestorage_subset_#{@date_time}.csv"
  end
  def enumerable
    THESIS_SUBSET.each do |i|
      yield @instance.find(i)
    end
  end
end


# Subset of Juptier Active Storage Blob and Item metadata
class JupiterItemActiveStorageBlobMetadataToCSVSubset < JupiterItemActiveStorageBlobMetadataToCSV 
  def initialize(output_directory)
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "jupiter_item_activestorage_subset_#{@date_time}.csv"
    @instance = Item
  end
  def enumerable
    ITEM_SUBSET.each do |i|
      yield @instance.find(i)
    end
  end
end

# Subset of Juptier Active Storage Blob and Thesis metadata
class JupiterThesisActiveStorageBlobMetadataToCSVSubset < JupiterItemActiveStorageBlobMetadataToCSV 
  def initialize(output_directory)
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "jupiter_thesis_activestorage_subset_#{@date_time}.csv"
    @instance = Thesis 
  end
  def enumerable
    THESIS_SUBSET.each do |i|
      yield @instance.find(i)
    end
  end
end


#JupiterCommunityMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/").run
#JupiterCollectionMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/").run
#JupiterItemMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/").run
#JupiterActiveStorageBlobMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/").run

JupiterThesisMetadataToCSVSubset.new("/tmp/").run
JupiterItemMetadataToCSVSubset.new("/tmp/").run
JupiterItemActiveStorageBlobMetadataToCSVSubset.new("/tmp/").run
JupiterThesisActiveStorageBlobMetadataToCSVSubset.new("/tmp/").run
