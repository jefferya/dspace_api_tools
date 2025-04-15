# Output a set of Jupiter metadata via Ruby irb script to output the metadata in CSV format
# Usage: irb -r ./juptiter_collection_metadata_to_CSV.rb
# Usage: RAILS_ENV=development bundle exec rails runner jupiter_collection_metadata_to_CSV.rb
# Runtime: approximately 10min (staging)

class JupiterBasicMetadataToCSV
  def initialize()
    @output_file = ""
    @instance
  end
  def run
    raise "Instance not set" unless @instance
    headers = @instance.new.decorate.attributes.keys
    CSV.open(@output_file, 'wb', write_headers: true, headers: headers) do |csv|
      @instance.find_each do |i|
        csv << i.decorate.attributes.values
      end
    end;
  end
end

# Jupiter Community Metadata
class JupiterCommunityMetadataToCSV < JupiterBasicMetadataToCSV
  def initialize(output_directory)
    super()
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = File.join(output_directory, "jupiter_community_#{@date_time}.csv")
    @instance = Community
  end
end

# Jupiter Collection metadata
class JupiterCollectionMetadataToCSV < JupiterBasicMetadataToCSV
  def initialize(output_directory)
    super()
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "jupiter_collection_#{@date_time}.csv"
    @instance = Collection 
  end
  def run
    raise "Instance not set" unless @instance
    # Need community label as DSapce doesn't include provanence on Communities
    headers = @instance.new.decorate.attributes.keys + ["community.title"]
    CSV.open(@output_file, 'wb', write_headers: true, headers: headers) do |csv|
      @instance.find_each do |i|
        community = Community.find(i.community_id); nil
        csv << i.decorate.attributes.values + [community.title]
      end;
    end
  end
end

# Jupiter Item metadata 
class JupiterItemMetadataToCSV < JupiterBasicMetadataToCSV
  def initialize(output_directory)
    super()
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @instance = Item 
    @output_file = output_directory + "jupiter_#{@instance.name}_#{@date_time}.csv"
  end
end

# Jupiter Item metadata 
class JupiterThesisMetadataToCSV < JupiterBasicMetadataToCSV
  def initialize(output_directory)
    super()
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @instance = Thesis 
    @output_file = output_directory + "jupiter_#{@instance.name}_#{@date_time}.csv"
  end
end


# Juptier Active Storage Blob and Item metadata
class JupiterItemActiveStorageBlobMetadataToCSV
  def initialize(output_directory)
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @instance = Item 
    @output_file = output_directory + "jupiter_#{@instance.name}_activestorage_#{@date_time}.csv"
  end
  def run
    # "provenance.ual.jupiterId.item" & "bitstream.sequenceId" labels need to align
    # with the DSpace CSV for use with pandas dataframe multi-index join
    # in the comparison script 
    headers = ["item.id",
                "item.title",
                "provenance.ual.jupiterId.item",
                "bitstream.sequenceId",
                "fileset_uuid",
                "key",
                "filename",
                "content_type",
                "metadata",
                "byte_size",
                "checksum",
                "created_at"] 
    CSV.open(@output_file, 'wb', write_headers: true, headers: headers) do |csv|
      @instance.find_each do |item|
        sequence_num = 0
          item.ordered_files.each do |f|
          sequence_num += 1
          csv << [item.id,
                  item.title,
                  item.id,
                  sequence_num,
                  f.fileset_uuid,
                  f.blob.key,
                  f.blob.filename,
                  f.blob.content_type,
                  f.blob.metadata,
                  f.blob.byte_size,
                  f.blob.checksum,
                  f.blob.created_at]
        end; nil
      end; nil
    end
  end
end

# Juptier Active Storage Blob and Thesis metadata
class JupiterThesisActiveStorageBlobMetadataToCSV < JupiterItemActiveStorageBlobMetadataToCSV 
  def initialize(output_directory)
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @instance = Thesis 
    @output_file = output_directory + "jupiter_#{@instance.name}_activestorage_#{@date_time}.csv"
  end
end


IRB.conf[:INSPECT_MODE] = false if Object.const_defined?('IRB')
ActiveRecord::Base.logger = nil

base_dir = "/era_tmp/delete_me_by_2025-05-15/"

# Community
JupiterCommunityMetadataToCSV.new(base_dir).run

# Collection
JupiterCollectionMetadataToCSV.new(base_dir).run

# Item
JupiterItemMetadataToCSV.new(base_dir).run
JupiterItemActiveStorageBlobMetadataToCSV.new(base_dir).run

# Thesis
JupiterThesisMetadataToCSV.new(base_dir).run
JupiterThesisActiveStorageBlobMetadataToCSV.new(base_dir).run
