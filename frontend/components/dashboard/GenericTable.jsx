import React from "react";
import PropTypes from "prop-types";


const GenericTable = props => {

  const { keys, headers, rows } = props.tableData;

  return (
    <table className="table">
      <thead>
        <tr>
          {
            keys.map(key => <td key={`header-${key}`}>{ headers[key] }</td> )
          }
        </tr>
      </thead>
      <tbody>
        {
          rows.map((row, index) => (
            <tr key={`row-${index}`}>
              {
                keys.map(key => <td key={`cell-${index}-${key}`}>{row[key]}</td>)
              }
            </tr>
          ))
        }
      </tbody>
    </table>
  );

}

GenericTable.defaultProps = {
  tableData: { keys: [], headers: [], rows: [] }
}

GenericTable.propTypes = {
  tableData: PropTypes.shape({ headers: PropTypes.array, rows: PropTypes.array, keys: PropTypes.array }).isRequired
}

export default GenericTable;
