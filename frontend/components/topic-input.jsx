import React, { useState } from 'react'
import Select from 'react-select';

const TopicInput = (props) => {
  const [selectedGuides, setSelectedGuides] = useState(props.value || []);

  const handleSelect = (selected) => {
    setSelectedGuides(selected);
  }

  const topicOptions = Array.from(props.topics);
  topicOptions.sort();

  return(
    <span>
      <select 
        type="hidden"
        name="topic_guides"
        multiple
        style={{display:"none"}}
        value={selectedGuides.map( t => t.value )}
      >
        {
          selectedGuides.map( t => {
            return (
              <option value={t.value} key={t.value}>{t.label}</option>
            )
          })
        }
      </select>

      <Select
        name="topics_input"
        isMulti={true}
        value={selectedGuides}
        onChange={handleSelect}
        options={topicOptions}
      />
    </span>
  )
}

export default TopicInput;
