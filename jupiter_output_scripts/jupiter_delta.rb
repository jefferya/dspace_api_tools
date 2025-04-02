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
        # change delta for Item & Thesis type converting end result
        # to DSpace/Scholaris key/value by extending the linked method
        # test if the key exsists in the object_changes and creating a new
        # structure in a new column listing the Scholaris key/value pairs to update
        # https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac#file-export_collections_csv-rb-L181-L196
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