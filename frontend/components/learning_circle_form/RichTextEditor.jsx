import React from 'react'
import PropTypes from 'prop-types'
// import { InputWrapper } from 'p2pu-components'
import tinymce from 'tinymce/tinymce';
import 'tinymce/icons/default';
import 'tinymce/themes/silver';
import 'tinymce/plugins/link';
import 'tinymce/plugins/lists';
import { Editor } from '@tinymce/tinymce-react';


const RichTextWithLabel = (props) => {
  const {
    name,
    id,
    label,
    value,
    initialValue,
    handleChange,
    required,
    disabled,
    errorMessage,
    helpText,
    classes,
    placeholder,
    ...rest
  } = props;

  const onChange = input => {
    props.handleChange({ [props.name]: input })
  }

  return (

      <Editor
         initialValue={initialValue}
         init={{
          height: 300,
          menubar: false,
          plugins: [
            'link lists'
          ],
          toolbar: 'undo redo | formatselect | bold italic | bullist numlist | link | removeformat',
          'valid_elements': 'p,h3,h4,h5,h6,strong,em,a,a[href|target=_blank|rel=noopener],ul,ol,li,div,span',
          'block_formats': 'Paragraph=p; Heading 1=h3; Heading 2=h4; Heading 3=h5',
         }}
         onEditorChange={onChange}
      />

  )
}

RichTextWithLabel.defaultProps = {
  type: 'text',
  value: "",
  initialValue: "",
  required: false,
  disabled: false,
  label: 'Textarea input',
  classes: '',
  handleChange: (input) => console.log("Implement a function to save input", input)
}

RichTextWithLabel.propTypes = {
  handleChange: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
  type: PropTypes.string,
  value: PropTypes.string,
  initialValue: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
  classes: PropTypes.string,
}

export default RichTextWithLabel;
