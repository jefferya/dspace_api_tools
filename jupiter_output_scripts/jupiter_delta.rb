# Delta a list of changes on Jupiter after a given date
# base on https://github.com/ualbertalib/jupiter/pull/3626/files

# Parent class from
# https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac#file-export_collections_csv-rb-L181-L196
class ItemCSVExporter < CollectionCSVExporter
  attr_accessor :easy_dspace_mapping
end

class ChangesReport

  def initialize(output_directory, date)
    @date = date 
    @output_file = output_directory + "#{date}_changes.csv" 
  end

  # Based on and try to reuse the mapping methods in the class
  # https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac#file-export_collections_csv-rb-L181-L196
  def map_change_event_to_scholaris_item(change_event)
      #result = CollectionCSVExporter.item_data_row(change_event.item)
      item = change_event.item.decorate
      ItemCSVExporter.new.easy_dspace_mapping do |method_key, _method_mapping|
        # keys starting with "manual_" are special cases that need to be handled differently
        jupiter_key = method_key.sub(/^manual_/,'')
        # only caputure value if the key exists in the list of object changes in the change event
        if change_event.object_changes.key?(jupiter_key) do
          value = if method_key.start_with?('manual_')
                    handle_manual_value(item, method_key)
                  else
                    item.send(method_key)
                  end
          if value.is_a?(Array)
            value.join('||')
          else
            value
          end
        end
      end 

  end

  def process_change_event(change_event)

    if change_event.type is Thesis do
    end
    else if change_event.item_type is Item do
      result = map_change_event_to_scholaris_item(change_event)
    end

    # return dictionary of key value pairs
    # where the key is the DSpace field name mapped from the Jupiter change event field
    # and the value is the DSpace field value transformed from the Jupiter change event new field value 
    return result
  end


  def perform()
    CSV.open(@output_file, 'wb') do |csv|
      csv << ['type', 'id', 'changed at', 'event', 'delta', 'scholaris_mapping']
      PaperTrail::Version.where(created_at: @date..).find_each do |row|
        # How to communicate key/value mapping differences from Jupiter to DSpace?
        # First part, add documentation describing how to use the output
        # Second part, add a new column that lists the new Scholaris key plus the newly transformed value 9if applicable)
        # Psuedocode: take the change delta for Item & Thesis type converting end result
        # to DSpace/Scholaris key/value by extending this method and class:
        # https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac#file-export_collections_csv-rb-L181-L196
        # I.e., test if the key exists in the object_changes and creating a new
        # structure in a new column listing the Scholaris key/value pairs to update
        scholaris_mapping = process_change_event(row)
        csv << [row.item_type, row.item_id, row.created_at, row.event, row.object_changes]
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

ChangesReport.new("/tmp/",Date.new(2005, 8, 8)).perform()