# Build a report with accopmanying file export for a specified collection
class JupiterActiveStorageBlobMetadataToCSV
  def initialize(output_directory)
    @date_time = Time.now.strftime("%Y-%m-%d_%H-%M-%S")
    @output_file = output_directory + "/jupiter_activestorage_#{@date_time}.csv"
    @output_file_dump = output_directory + "/jupiter_files_#{@date_time}"
    # @member_of_paths_successful_grants = '"5a69bd79-86e9-4208-82d9-917c95873ed5/2f3a8f93-63fa-434e-af51-0bda6e245be5"'
    # Test local
    #@member_of_paths_successful_grants = '"b075613c-16a6-49d2-8cea-1ffb55ea4e53/4c99b4cf-e44e-4f41-b139-958d3911ec60"'
    # Production
    @member_of_paths_successful_grants = '"8f446adf-bae4-49f5-84b7-6195718ca844/18826f1d-a1f7-4466-9f0e-8ae88350b984"'
  end
  def run
    Dir.mkdir(@output_file_dump) unless File.exists?(@output_file_dump)
    headers = ["item.id",
                "item.url",
                "item.title",
                "item.creators",
                "item.created_at",
                "item.updated_at",
                "bitstream.sequenceId",
                "file.key",
                "filename",
                "byte_size",
                "checksum",
                "created_at",
                "updated_at",
                "file_download_url",
                "local_file_path",
              ] 
    CSV.open(@output_file, 'wb', write_headers: true, headers: headers) do |csv|
      # member_of_paths is defined in the PostgreSQL DB schema as "json[]" (PostgreSQL array of JSON objects)
      # Why not use the "json" data type as JSON can contain lists of things and the "@>" operator can be used rather than
      # casting JSON to TEXT in where clauses (or store member_of_path strings as varchar[] for a more efficient DB structure)?
      # Item.where("member_of_paths @> {'8f446adf-bae4-49f5-84b7-6195718ca844/18826f1d-a1f7-4466-9f0e-8ae88350b984'}").find_each do |item|
      # Item.where("'\"b075613c-16a6-49d2-8cea-1ffb55ea4e53/4c99b4cf-e44e-4f41-b139-958d3911ec60\"'::TEXT = any(member_of_paths::text[])").find_each do |item|
      # Item.where("?::TEXT = any(member_of_paths::text[])", '"b075613c-16a6-49d2-8cea-1ffb55ea4e53/4c99b4cf-e44e-4f41-b139-958d3911ec60"').find_each do |item|
      Item.where("?::TEXT = any(member_of_paths::text[])", @member_of_paths_successful_grants).find_each do |item|
        sequence_num = 0
        item.ordered_files.each do |f|
          sequence_num += 1
          file_path = @output_file_dump + "/#{f.blob.filename}"
          # check for duplicate file names
          file_path = "#{file_path}_duplicate_name_#{item.id}" if File.exist?(file_path)
          csv << [item.id,
                  Rails.application.routes.url_helpers.item_url(id: item.id),
                  item.title,
                  item.creators,
                  item.created_at,
                  item.updated_at,
                  sequence_num,
                  f.blob.key,
                  f.blob.filename,
                  f.blob.byte_size,
                  f.blob.checksum,
                  f.blob.created_at,
                  Rails.application.routes.url_helpers.file_download_item_url(id: f.record.id, file_set_id: f.fileset_uuid),
                  file_path]
          # Write the file to disk
          File.open(file_path, 'wb') do |file|
            file.write(f.blob.download)
          end
        end
      end
    end
  end
end

############
JupiterActiveStorageBlobMetadataToCSV.new("/era_tmp/delete_me_by_2025-04-15/successful_grants/").run # change to /era

# Next steps:
# 1. download local copy of rclone in home directory
#   a. curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
#   b. unzip rclone-current-linux-amd64.zip
#   c. cd rclone-*-linux-amd64
# 2. Configure rclone to connect to the your Google Drive: https://rclone.org/drive/
#   a. ./rclone config
#     * ensure the name of the remote useable in the rclone command below, e.g., "gdrive"
# 3. Test
#   a. ./rclone lsd "gdrive": 
# 4. Run
#   a. ./rclone copy  /era_tmp/delete_me_by_2025-04-15/successful_grants "gdrive": --progress