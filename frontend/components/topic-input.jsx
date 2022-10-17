import React, { useState } from 'react'
import Select from 'react-select';

const TopicInput = (props) => {
  const [selectedTopics, setSelectedTopics] = useState(props.value || []);

  const handleSelect = (selected) => {
    setSelectedTopics(selected);
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
        value={selectedTopics.map( t => t.value )}
      >
        {
          selectedTopics.map( t => {
            return (
              <option value={t.value} key={t.value}>{t.label}</option>
            )
          })
        }
      </select>

      <Select
        name="topics_input"
        isMulti={true}
        value={selectedTopics}
        onChange={handleSelect}
        options={topicOptions}
      />
    </span>
  )
}

export default TopicInput;
