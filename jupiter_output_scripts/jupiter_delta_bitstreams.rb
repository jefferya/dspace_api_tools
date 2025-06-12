# Bitstream Delta: list of bitstream changes on Jupiter after a given date
#   RAILS_ENV=development bundle exec rails runner jupiter_delta_bitstreams.rb 

class BitstreamChangeReport

  def initialize(output_directory, date)
    @date = date 
    @output_file = File.join(output_directory, "#{date}_bitstream_changes.csv")
  end

  def perform()
    CSV.open(@output_file, 'wb') do |csv|
      # Header
      csv << [
        'attachment.record_type',
        'attachement.record_id',
        'attachement.fileset_uuid',
        'attachment.created_at',
        'blob.id',
        'blob.created_at',
        'blob.filename',
        'blob.content_type',
        'blob.byte_size',
        'blob.checksum'
      ]
      #ActiveStorage::Blob.where('created_at > ?', @date).each do |blob|
        #attachment = ActiveStorage::Attachment.find_by(blob_id: blob.id)
      ActiveStorage::Attachment.where('created_at > ?', @date).find_each do |attachment| 
        blob = attachment.blob
        csv << [
          attachment.record_type,
          attachment.record_id,
          attachment.fileset_uuid,
          attachment.created_at,
          blob.id,
          blob.created_at,
          blob.filename,
          blob.content_type,
          blob.byte_size,
          blob.checksum
        ]
      end
    end
  end

end

BitstreamChangeReport.new("/tmp/",Date.new(2025, 3, 24)).perform();
