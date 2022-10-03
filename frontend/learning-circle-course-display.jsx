import React from 'react'
import ReactDOM from 'react-dom'
import LearningCircleCard from 'p2pu-components/dist/LearningCircles/LearningCircleCard'

const element = document.getElementById('learning-circle-course-display')
const learningCircles = element.dataset.learningCircles;

ReactDOM.render(
    <div>
        {
            learningCircles.map((lc) => 
                <LearningCircleCard learningCircle={lc} locale={} onSelectResult={} />
            )
        }
    </div>, 
    element
)
