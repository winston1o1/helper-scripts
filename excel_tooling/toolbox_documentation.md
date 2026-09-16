
# excel_toolbox Class Documentation

A utility class that provides helper functions for automatically calculating and applying column widths in Excel worksheets generated using `pandas` and Excel writers like `xlsxwriter`.

## Methods

---

### `excel_toolbox.calculate_column_width(dataset)`

**Description:**  
Calculates the optimal column width for each column in a pandas DataFrame based on the length of the column header and the longest item in the column.

**Parameters:**  
- `dataset` (`pd.DataFrame`): A pandas DataFrame whose column widths need to be calculated.

**Returns:**  
- `List[int]`: A list of integers representing the calculated width for each column in the DataFrame.

**Logic:**  
- For each column:
  - Compute the length of the column name plus a padding of 3 characters.
  - Find the length of the longest string in that column.
  - Set the column width to the maximum of the above two values.

**Example:**  
```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob"],
    "Occupation": ["Data Scientist", "Engineer"]
})

widths = excel_toolbox.calculate_column_width(df)
# widths might be something like [8, 15]
```

---

### `excel_toolbox.auto_fit_column_width(column_sizes, worksheet)`

**Description:**  
Applies the calculated column widths to a given worksheet.

**Parameters:**  
- `column_sizes` (`List[int]`): A list of integers specifying the desired width of each column.
- `worksheet`: A worksheet object, typically retrieved from `writer.sheets[sheet_name]` in `pandas.ExcelWriter`.

**Returns:**  
- The modified `worksheet` with adjusted column widths.

**Example:**  
```python
with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    worksheet = writer.sheets['Sheet1']
    widths = excel_toolbox.calculate_column_width(df)
    excel_toolbox.auto_fit_column_width(widths, worksheet)
```

