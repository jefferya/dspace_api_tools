# Ruby irb script to output the metadata of a collection in CSV format
# Usage: irb -r ./juptiter_collection_metadata_to_CSV.rb

class JupiterBasicMetadataToCSV
  def initialize()
    @output_file = ""
    @instance
  end
  def run
    reaise "Instance not set" unless @instance
    headers = @instance.new.decorate.attributes.keys
    CSV.open(@output_file, 'wb', write_headers: true, headers: headers) do |csv|
      @instance.find_each do |i|
        csv << i.decorate.attributes.values
      end
    end
  end
end

class JupiterCommunityMetadataToCSV < JupiterBasicMetadataToCSV
  def initialize(output_directory)
    super()
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = File.join(output_directory, "jupiter_community_#{@date_time}.csv")
    @instance = Community
  end
end

class JupiterCollectionMetadataToCSV < JupiterBasicMetadataToCSV
  def initialize(output_directory)
    super()
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "jupiter_collection_#{@date_time}.csv"
    @instance = Collection 
  end
end

JupiterCommunityMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/").run
JupiterCollectionMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/").run
