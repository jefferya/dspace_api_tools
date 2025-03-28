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


# Juptier Active Storage Blob and Item metadata
class JupiterActiveStorageBlobMetadataToCSV
  def initialize(output_directory)
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "jupiter_activestorage_#{@date_time}.csv"
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

# Subset of Juptier Active Storage Blob and Item metadata
class JupiterActiveStorageBlobMetadataToCSVSubset < JupiterActiveStorageBlobMetadataToCSV 
  def initialize(output_directory)
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "jupiter_activestorage_subset_#{@date_time}.csv"
    @instance = Item
  end
  def enumerable
    ITEM_SUBSET.each do |i|
      yield @instance.find(i)
    end
  end
end

#JupiterCommunityMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/").run
#JupiterCollectionMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/").run
#JupiterItemMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/").run
#JupiterActiveStorageBlobMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/").run

JupiterItemMetadataToCSVSubset.new("/tmp/").run
JupiterActiveStorageBlobMetadataToCSVSubset.new("/tmp/").run
