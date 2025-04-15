# Delta a list of changes on Jupiter after a given date
# base on https://github.com/ualbertalib/jupiter/pull/3626/files
#   RAILS_ENV=development bundle exec rails runner jupiter_delta.rb 

require_relative 'helpers/file-export_collections_csv'
require 'json'


# Parent class from
# https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac#file-export_collections_csv-rb-L181-L196
class ItemCSVExporter < CollectionCSVExporter
  attr_accessor :easy_dspace_mapping

  def easy_dspace_mapping
    @easy_dspace_mapping.each do |key, value|
      yield key, value
    end
  end

end

class ChangesReport

  def initialize(output_directory, date)
    @date = date 
    @output_file = File.join(output_directory, "#{date}_changes.csv")
  end

  # Based on and try to reuse the mapping methods in the class
  # https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac#file-export_collections_csv-rb-L181-L196
  def map_change_event_to_scholaris_item(change_event, obj)

    scholaris_mapped_change_event = {} 
    itemTranslation = ItemCSVExporter.new
    begin 
      item = obj.decorate
      itemTranslation.easy_dspace_mapping do |method_key, _method_mapping|
        # keys starting with "manual_" are special cases that need to be handled differently
        jupiter_key = method_key.sub(/^manual_/,'')
        # only caputure value if the key exists in the list of object changes in the change event
        if change_event.object_changes && change_event.object_changes.key?(jupiter_key)
          value = if method_key.start_with?('manual_')
                    itemTranslation.handle_manual_value(item, method_key)
                  else
                    item.send(method_key)
                  end
          scholaris_mapped_change_event[_method_mapping] = value
        end
      end;
    rescue NoMethodError
      puts "Mapping Error on jupiter ID #{change_event.item_id} of type #{change_event.item_type} and event #{change_event.event}"
    end
    return scholaris_mapped_change_event
  end

  def process_change_event(change_event, obj)

    if change_event.event == "destroy"
      result = {}
    else
      if change_event.item_type == "Thesis"
        result = '{"Thesis: scholaris mapping unsupported"}'
      elsif change_event.item_type == "Item"
        result = map_change_event_to_scholaris_item(change_event, obj)
      elsif change_event.item_type == "Community"
        result = '{"Community: scholaris mapping unsupported"}'
      elsif change_event.item_type == "Collection"
        result = '{"Collection: scholaris mapping unsupported"}'
      else
        result = '{"Unsupported type"}'
      end
    end

    # return dictionary of key value pairs
    # where the key is the DSpace field name mapped from the Jupiter change event field
    # and the value is the DSpace field value transformed from the Jupiter change event new field value 
    return result
  end


  def perform()
    CSV.open(@output_file, 'wb') do |csv|
      csv << ['type', 'change_id', 'jupiter_id', 'is_jupiter_currently_readonly', 'read_only_event', 'changed at', 'event', 'jupiter delta', 'scholaris mapped delta', 'jupiter delta formatted', 'scholaris mapped delta formatted']
      PaperTrail::Version.where(created_at: @date..).find_each do |row|
        # How to communicate key/value mapping differences from Jupiter to DSpace?
        # First part, add documentation describing how to use the output
        # Second part, add a new column that lists the new Scholaris key plus the newly transformed value 9if applicable)
        # Psuedocode: take the change delta for Item & Thesis type converting end result
        # to DSpace/Scholaris key/value by extending this method and class:
        # https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac#file-export_collections_csv-rb-L181-L196
        # I.e., test if the key exists in the object_changes and creating a new
        # structure in a new column listing the Scholaris key/value pairs to update
        obj = row.item
        read_only = "True" if obj && obj.read_only?
        read_only_event = "True" if row.object_changes && row.object_changes.keys.to_set == ["updated_at", "read_only"].to_set
        scholaris_mapping = process_change_event(row, obj)
        csv << [row.item_type, row.id, row.item_id, read_only, read_only_event, row.created_at, row.event, row.object_changes, scholaris_mapping, JSON.pretty_generate(row.object_changes), JSON.pretty_generate(scholaris_mapping)]
      end
    end

    i = Item.updated_on_or_after(@date).count
    t = Thesis.updated_on_or_after(@date).count
    cl = Collection.updated_on_or_after(@date).count
    cm = Community.updated_on_or_after(@date).count
    summary = "#{i} items, #{t} theses, #{cl} collections and #{cm} communities were created or modified."
    puts(summary)

  end

end

ChangesReport.new("/era_tmp/delete_me_by_2025-05-14/",Date.new(2025, 3, 15)).perform()