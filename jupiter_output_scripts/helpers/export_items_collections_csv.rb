# From: https://github.com/lagoan/era_export/blob/main/export_items_collections_csv.rb
# with the removal of "CollectionCSVItemExporter.new.run" to allow a "require"

class CollectionCSVItemExporter

  def initialize

    @easy_item_type_mapping = {
        # Values to check when there are multiple entries
        'http://purl.org/ontology/bibo/Article' => 'http://purl.org/coar/resource_type/c_6501',
        'http://purl.org/ontology/bibo/status#draft' => 'http://purl.org/coar/version/c_b1a7d7d4d402bcce',
        'http://vivoweb.org/ontology/core#submitted' => 'http://purl.org/coar/version/c_71e4c1898caa6e32',
        # 'http://purl.org/ontology/bibo/Article' => 'http://purl.org/coar/resource_type/c_6501',
        'http://purl.org/ontology/bibo/status#published' => 'http://purl.org/coar/version/c_970fb48d4fbd8a85',
        # Values mapped one to one
        'http://purl.org/ontology/bibo/Book' => 'http://purl.org/coar/resource_type/c_2f33',
        'http://purl.org/ontology/bibo/Chapter' => 'http://purl.org/coar/resource_type/c_3248',
        'http://purl.org/ontology/bibo/Image' => 'http://purl.org/coar/resource_type/c_c513',
        'http://purl.org/ontology/bibo/Report' => 'http://purl.org/coar/resource_type/c_93fc',
        'http://terms.library.ualberta.ca/researchMaterial' => 'http://purl.org/coar/resource_type/c_1843',
        'http://vivoweb.org/ontology/core#Presentation' => 'http://purl.org/coar/resource_type/R60J-J5BD',
        'http://vivoweb.org/ontology/core#ConferencePoster' =>  'http://purl.org/coar/resource_type/c_6670',
        'http://vivoweb.org/ontology/core#Dataset' => 'http://purl.org/coar/resource_type/c_ddb1',
        'http://vivoweb.org/ontology/core#Review' => 'http://purl.org/coar/resource_type/c_efa0',
        'http://terms.library.ualberta.ca/learningObject' => 'http://purl.org/coar/resource_type/c_e059'
    }

    @easy_dspace_mapping = {
      # Alphabetical order
      # 'manual_collections' => 'collections', # Will be adding identifiers when processing SAF
      'creators' => 'dc.contributor.author',
      'contributors' => 'dc.contributor.other',
      'spatial_subjects' => 'dc.coverage.spatial',
      'temporal_subjects' => 'dc.coverage.temporal',
      'created' => 'dc.date.issued',
      'description' => 'dc.description',
      'manual_doi' => 'dc.identifier.doi',
      'manual_languages' => 'dc.language.iso',
      # All items in jupiter have this value as nil. Also, Dspace does not use it
      'publisher' => 'dc.publisher',
      'related_link' => 'dc.relation',
      'is_version_of' => 'dc.relation.isversionof',
      'rights' => 'dc.rights',
      'license' => 'dc.rights.uri',
      'source' => 'dcterms.source',
      'subject' => 'dc.subject',
      'title' => 'dc.title',
      'alternative_title' => 'dc.title.alternative',
      'manual_item_type' => 'dc.type', # Merge item_type and publication_status
      'visibility' => 'ual.jupiterAccess',
      'manual_filename' =>	"filename",
      'manual_jupiter_filename' => 'ual.jupiterFilename',
      'manual_embargo_end_date' => 'local.embargo.terms',
      # 'visibility_after_embargo' => 'local.embargo.postLiftAccess', # No longer in use, we may add it later
      'depositor' => 'ual.depositor',
      # 'embargo_history' => 'dc.description.provenance',
      'manual_edit_history' => 'dc.description.provenance',
      'fedora3_handle' => 'ual.fedora3Handle',
      'fedora3_uuid' => 'ual.fedora3UUID',
      'hydra_noid' => 'ual.hydraNoid',
      'manual_ingest_batch' => 'ual.ingestBatch', # Merge ingest_batch merge two fields "http://terms.library.ualberta.ca/ingestBatch and batch_ingest_id"
      'member_of_paths' => 'ual.jupiterCollection',
      'record_created_at' => 'ual.date.createdInERA',
      'created_at' => 'ual.date.createdInJupiter',
      'updated_at' => 'ual.date.updatedInJupiter',
      'id' => 'ual.jupiterId',
      'manual_stat_downloads' => 'ual.stats.jupiterDownloads', # Stats
      'manual_stat_views' => 'ual.stats.jupiterViews', # Stats
      # 'manual_logo' => 'ual.jupiterThumbnail', # We are already saving the primary file on the contents file of the SAF
      'manual_owner_id' => 'ual.owner',
      # Values used to process files
      'manual_file_paths' => 'file:paths',
      'manual_thumbnail_index' => 'thumbnail:index'
      # Do not include:
      # 'sort_year' => 'ual.sortYear',
    }

    @easy_language_mapping = {
      'http://id.loc.gov/vocabulary/iso639-2/eng' => 'en',
      'http://id.loc.gov/vocabulary/iso639-2/fre' => 'fr',
      'http://id.loc.gov/vocabulary/iso639-2/ger' => 'de',
      'http://id.loc.gov/vocabulary/iso639-2/ita' => 'it',
      'http://id.loc.gov/vocabulary/iso639-2/jpn' => 'ja',
      'http://id.loc.gov/vocabulary/iso639-2/spa' => 'es',
      'http://id.loc.gov/vocabulary/iso639-2/zho' => 'zh',
      'http://id.loc.gov/vocabulary/iso639-2/ukr' => 'uk',
      'http://id.loc.gov/vocabulary/iso639-2/rus' => 'ru',
      'http://id.loc.gov/vocabulary/iso639-2/zxx' => 'No linguistic content',
      'http://terms.library.ualberta.ca/other' => 'other'
    }
  end

  def handle_manual_value(item, key)
    case key
    when 'manual_filename'
      item.ordered_files.map { |file| file.filename.to_s }
    when 'manual_jupiter_filename'
      # Here we are using the same information as manual_filename. This information will not be modified
      # at a later time to add the permissions. The permissions are added in the next step using the 
      # script ``process_collection_for_saf.rb``.
      item.ordered_files.map { |file| file.filename.to_s }
    when 'manual_stat_downloads'
      Statistics.for(item_id: item.id)[1]
    when 'manual_stat_views'
      Statistics.for(item_id: item.id)[0]
    when 'manual_file_paths'
      item.ordered_files.map { |file| ActiveStorage::Blob.service.path_for(file.key) }
    when 'manual_item_type'
      # Merging item_type and publication_status. Ignore nil or blank values
      ([item.item_type] + Array(item.publication_status)).reject(&:blank?).map { |type| @easy_item_type_mapping[type] }.join(' ')
    when 'manual_logo'
      logo_file = item.files.find_by(id: item.logo_id)
      logo_file.filename.to_s if logo_file.present?
    when 'manual_ingest_batch'
      # Merging ingest_batch and batch_ingest_id. Ignore nil or blank values
      [item.ingest_batch, item.batch_ingest_id].reject(&:blank?)
    when 'manual_owner_id'
      item.owner.email if item.owner.present?
    # when 'manual_collections'
    #   item.member_of_paths.map{ |path| Collection.find(path.split('/')[1]).title }
    when 'manual_edit_history'
      # Mix item.embargo_history and item.versions
      embargo_history = {
        jupiter_embargo_history: item.embargo_history
      }.to_json.to_s unless item.embargo_history.blank?

      cleaned_up_edit_history = clean_up_edit_history(item.versions)

      edit_history = cleaned_up_edit_history.present? ? {
        jupiter_edit_history: cleaned_up_edit_history
      }.to_json.to_s : nil

      [embargo_history, edit_history].reject(&:blank?).join('||')
    when 'manual_thumbnail_index'
      item.files.find_index { |file| file.id == item.logo_id }
    when 'manual_embargo_end_date'
      item.embargo_end_date.strftime('%F') if item.embargo_end_date.present?
    when 'manual_doi'
      item.doi.gsub(/^doi:/, 'https://doi.org/') if item.doi.present?
    when 'manual_languages'
      item.languages.map { |language| @easy_language_mapping[language] }.join('||')
    end
  end

  def clean_up_edit_history(versions)
    data = versions.select { |version| version.changeset.any? }.map do |version|
      {
        event: version.event,
        date: version.created_at,
        changes: version.changeset,
        edited_by: user_info(version.whodunnit)
      }
    end

    first_filter = data.map do |entry|
      # Remove specified keys from 'changes'
      if entry[:changes]
        entry[:changes].delete('aasm_state')
        entry[:changes].delete('logo_id')
      end

      entry
    end

    # We do not want to keep changesets with only update_at values
    first_filter.reject do |entry|
      entry[:changes].keys.length == 1 && entry[:changes].keys.first == 'updated_at'
    end
  end

  def user_info(whodunnit)
    if whodunnit.present?
      user = User.find_by(id: whodunnit)
      user_info = if user.present?
                    user.email
                  else
                    whodunnit
                  end
    else
      user_info = 'Unknown'
    end

    user_info
  end

  def remove_xml_invalid_characters(value)
    value.gsub(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F-\u009F]/, '')
  end

  def item_data_row(item)
    # item = item.decorate
    @easy_dspace_mapping.map do |method_key, _method_mapping|
      # keys starting with "manual_" are special cases that need to be handled differently
      value = if method_key.start_with?('manual_')
                handle_manual_value(item, method_key)
              else
                item.send(method_key)
              end
      value = value.join('||') if value.is_a?(Array)

      if value.is_a?(String)
        remove_xml_invalid_characters(value)
      else
        value
      end
    end
  end

  def prepare_headers
    @easy_dspace_mapping.each_value.map { |value| value }
  end

  def run
    item_headers = prepare_headers
    directory_path = 'era_export'
    FileUtils.mkdir_p(directory_path)
    # Export all collections, skipping items that appear in more than one collection
    Collection.find_each do |collection|
      # Skip collections that do not have any items
      # Sometimes we will can have empty files if the collection contains items belonging to multiple collections
      next if collection.member_items.empty?

      CSV.open("#{directory_path}/items_#{collection.id}.csv", 'wb', write_headers: true, headers: item_headers) do |csv|
        collection.member_items.each do |item|
          # Skip if item in multiple collections, this will be added in another SAF
          next if item.member_of_paths.size > 1

          csv << item_data_row(item)
        end
      end
    end

    # Export a single CSV with all items that appear in more than one collection
    CSV.open("#{directory_path}/items_in_multiple_collections.csv", 'wb', write_headers: true, headers: item_headers) do |csv|
      Item.where('array_length(member_of_paths, 1) > 1').find_each do |item|
        csv << item_data_row(item)
      end
    end
  end
end
