
class toolbox(object):
    def calculate_column_width(dataset):
        '''
        Arg: dataset - Expects a panda dataframe (pd.DataFrame)\n
        Return: List of sizes (int) for each column
        '''
        cols = dataset.columns.to_list()
        col_sizes = []
        for i in range(len(cols)):
            # pad the column name length by 3
            col_word_length = len(cols[i]) + 3
            # Get the logest word in a given column
            longest_word_in_col = sorted([len(str(char)) for char in dataset[cols[i]]])[-1]
            if col_word_length >= longest_word_in_col:
                col_size = col_word_length
            else:
                col_size = longest_word_in_col

            col_sizes.append(col_size)
            
        return col_sizes

    def auto_fit_column_width(column_sizes,worksheet):
        '''
        Arg: column_sizes - Expects a list in sizes of type "int"\n
        Arg: worksheet - Expects a worksheet. Can be from writer.sheet(pandas writer) \n
        Return: Resized worksheet
        '''
        c = 0
        for column_size in column_sizes:
            worksheet.set_column(c, c, column_size)
            c += 1

        return worksheet