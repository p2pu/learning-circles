import React from 'react'

import LearningCircleCard from 'p2pu-components/dist/LearningCircles/LearningCircleCard'
import 'p2pu-components/dist/build.css';

const CourseLearningCircles = ({ learningCircles, defaultImageUrl }) => {
  return(
    <div className="row grid">
      {
        learningCircles.map((lc) => 
          <LearningCircleCard key={lc.id} learningCircle={lc} defaultImageUrl={defaultImageUrl} />
        )
      }
    </div>
  )
}

export default CourseLearningCircles
