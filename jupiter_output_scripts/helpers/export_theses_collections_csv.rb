# From https://github.com/lagoan/era_export/blob/main/export_theses_collections_csv.rb
# with the last line removed: "CollectionCSVThesisExporter.new.run" to all a "require"

class CollectionCSVThesisExporter

  def initialize

    @easy_thesis_dspace_mapping = {
      'supervisors' => 'dc.contributor.advisor',
      'dissertant' => 'dc.contributor.author',
      'committee_members' => 'dc.contributor.other',
      'manual_date_accepted' => 'dcterms.dateAccepted',
      # graduation_date is used to fill 2 values in DSpace
      'manual_date_issued' => 'dc.date.issued',
      'manual_graduation_date' => 'dc.date.created',
      'manual_date_submitted' => 'dc.date.submitted',
      'abstract' => 'dc.description.abstract',
      'manual_edit_history' => 'dc.description.provenance',
      # 'embargo_history' => '',
      # 'edit history' => '',
      'manual_doi' => 'dc.identifier.doi',
      'manual_language' => 'dc.language.iso',
      'is_version_of' => 'dc.relation.isversionof',
      'rights' => 'dc.rights',
      'subject' => 'dc.subject',
      'title' => 'dc.title',
      'alternative_title' => 'dc.title.alternative',
      'manual_thesis_type' => 'dc.type', # Static value 'http://purl.org/coar/resource_type/c_46ec'
      'visibility' => 'ual.jupiterAccess',
      # 'northern_north_america_filename' => '',
      # 'northern_north_america_item_id' => '',
      # 'entity_type' => '',
      'manual_filename' => 'filename',
      'manual_embargo_end_date' => 'local.embargo.terms',
      # 'visibility_after_embargo' => '',
      # 'sort_year' => '',
      # 'aasm_state' => '',
      # '-' => 'relation.isAuthorOfPublication', # Dynamic value. Use identifier generated from depositors imported as Person entities
      'specialization' => 'thesis.degree.discipline',
      'institution' => 'thesis.degree.grantor',
      'thesis_level' => 'thesis.degree.level',
      'degree' => 'thesis.degree.name',
      'record_created_at' => 'ual.date.createdInERA',
      'created_at' => 'ual.date.createdInJupiter',
      'updated_at' => 'ual.date.updatedInJupiter',
      'departments' => 'ual.department',
      'depositor' => 'ual.depositor',
      'fedora3_handle' => 'ual.fedora3Handle',
      'fedora3_uuid' => 'ual.fedora3UUID',
      'hydra_noid' => 'ual.hydraNoid',
      'ingest_batch' => 'ual.ingestBatch',
      'member_of_paths' => 'ual.jupiterCollection',
      'manual_jupiter_filename' => 'ual.jupiterFilename',
      # 'date_ingested' => 'ual.jupiterDateCreated',
      'id' => 'ual.jupiterId',
      # 'logo' => 'ual.jupiterThumbnail', # We are already saving the primary file on the contents file of the SAF
      'manual_owner_id' => 'ual.owner',
      'proquest' => 'ual.proquestId',
      'manual_stat_downloads' => 'ual.stats.jupiterDownloads',
      'manual_stat_views' => 'ual.stats.jupiterViews',
      'unicorn' => 'ual.unicornId',
      'manual_file_paths' => 'file:paths',
      'manual_thumbnail_index' => 'thumbnail:index'
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

  def handle_manual_value(thesis, key)
    case key
    when 'manual_edit_history'
      # Mix thesis.embargo_history and thesis.versions
      embargo_history = {
        jupiter_embargo_history: thesis.embargo_history
      }.to_json.to_s unless thesis.embargo_history.blank?

      cleaned_up_edit_history = clean_up_edit_history(thesis.versions)

      edit_history = cleaned_up_edit_history.present? ? {
        jupiter_edit_history: cleaned_up_edit_history
      }.to_json.to_s : nil

      [embargo_history, edit_history].reject(&:blank?).join('||')
    when 'manual_thesis_type'
      'http://purl.org/coar/resource_type/c_46ec'
    when 'manual_filename'
      thesis.ordered_files.map { |file| file.filename.to_s }
    when 'manual_jupiter_filename'
      thesis.ordered_files.map { |file| file.filename.to_s }
    when 'manual_owner_id'
      thesis.owner.email if thesis.owner.present?
    when 'manual_embargo_end_date'
      thesis.embargo_end_date.strftime('%F') if thesis.embargo_end_date.present?
    when 'manual_file_paths'
      thesis.ordered_files.map { |file| ActiveStorage::Blob.service.path_for(file.key) }
    when 'manual_thumbnail_index'
      thesis.files.find_index { |file| file.id == thesis.logo_id }
    when 'manual_stat_downloads'
      Statistics.for(item_id: thesis.id)[1]
    when 'manual_stat_views'
      Statistics.for(item_id: thesis.id)[0]
    when 'manual_date_issued'
      # Here we assume graduation_date is of format YYYY ot YYYY-MM
      thesis.graduation_date
    when 'manual_graduation_date'
      # This helper will give us dates as Spring, 2011
      ApplicationController.helpers.humanize_date(thesis.graduation_date)
    when 'manual_language'
      # thesis.languages.map { |language| @easy_language_mapping[language] }.join('||')
      @easy_language_mapping[thesis.language]
    when 'manual_doi'
      thesis.doi.gsub(/^doi:/, 'https://doi.org/') if thesis.doi.present?
    when 'manual_date_accepted'
      thesis.date_accepted.strftime('%F') if thesis.date_accepted.present?
    when 'manual_date_submitted'
      thesis.date_submitted.strftime('%F') if thesis.date_submitted.present?
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

  def thesis_data_row(thesis)
    # thesis = thesis.decorate
    @easy_thesis_dspace_mapping.map do |method_key, _method_mapping|
      # keys starting with "manual_" are special cases that need to be handled differently
      value = if method_key.start_with?('manual_')
                handle_manual_value(thesis, method_key)
              else
                thesis.send(method_key)
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
    @easy_thesis_dspace_mapping.each_value.map { |value| value }
  end

  def run
    thesis_headers = prepare_headers
    directory_path = 'era_export'
    FileUtils.mkdir_p(directory_path)
    # Export all collections, skipping theses that appear in more than one collection
    Collection.find_each do |collection|
      # Skip collections that do not have any theses
      # Sometimes we will can have empty files if the collection contains theses belonging to multiple collections
      next if collection.member_theses.empty?

      CSV.open("#{directory_path}/theses_#{collection.id}.csv", 'wb', write_headers: true, headers: thesis_headers) do |csv|
        collection.member_theses.each do |thesis|
          # Skip if thesis in multiple collections, this will be added in another SAF
          next if thesis.member_of_paths.size > 1

          csv << thesis_data_row(thesis)
        end
      end
    end

    # Export a single CSV with all Thesis that appear in more than one collection
    CSV.open("#{directory_path}/theses_in_multiple_collections.csv", 'wb', write_headers: true, headers: thesis_headers) do |csv|
      Thesis.where('array_length(member_of_paths, 1) > 1').find_each do |thesis|
        csv << thesis_data_row(thesis)
      end
    end
  end
end
