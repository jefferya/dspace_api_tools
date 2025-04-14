# Output Jupiter statistics via Ruby irb script in CSV format
# Usage: irb -r ./juptiter_statistics_metadata_to_CSV.rb
# Usage: RAILS_ENV=development bundle exec rails runner juptiter_statistics_metadata_to_CSV.rb 
:

class JupiterBaseStatisticsToCSV
  def initialize()
    @output_file = ""
    @instance
  end
  def run
    raise "Instance not set" unless @instance
    headers = ['id', 'label', 'ual.stats.jupiterViews', 'ual.stats.jupiterDownloads'] 
    CSV.open(@output_file, 'wb', write_headers: true, headers: headers) do |csv|
      @instance.find_each do |i|
        # Statistics views then downloads in the returned arry (jupiter/app/services/statistics.rb)
        csv << [i.id, i.title] + Statistics.for(item_id: i.id)
      end
    end;
  end
end

# Jupiter Item metadata 
class JupiterItemStatisticsToCSV < JupiterBaseStatisticsToCSV
  def initialize(output_directory)
    super()
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @instance = Item 
    @output_file = output_directory + "jupiter_#{@instance.name}_#{@date_time}.csv"
  end
end

IRB.conf[:INSPECT_MODE] = false
ActiveRecord::Base.logger = nil

# Item data model
JupiterItemStatisticsToCSV.new("/tmp/").run