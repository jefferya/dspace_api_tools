# Delta a list of changes on Jupiter after a given date
# base on https://github.com/ualbertalib/jupiter/pull/3626/files


class ChangesReport

  def initialize(output_directory, date)
    @date = date 
    @output_file = output_directory + "#{date}_changes.csv" 
  end

  def perform()
    CSV.open(@output_file, 'wb') do |csv|
      csv << ['type', 'id', 'changed at', 'event', 'delta']
      PaperTrail::Version.where(created_at: @date..).find_each do |row|
        # How to communicate key/value mapping differences from Jupiter to DSpace?
        # First part, add documentation describing how to use the output
        # Second part, add a new column that lists the new Scholaris key plus the newly transformed value 9if applicable)
        # Psuedocode: take the change delta for Item & Thesis type converting end result
        # to DSpace/Scholaris key/value by extending this method and class:
        # https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac#file-export_collections_csv-rb-L181-L196
        # I.e., test if the key exists in the object_changes and creating a new
        # structure in a new column listing the Scholaris key/value pairs to update
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