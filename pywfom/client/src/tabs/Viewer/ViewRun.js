import {useEffect, useState} from 'react';

import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Image from 'react-bootstrap/Image';

export default function ViewRun(props){

  useEffect(() => {
    fetch(`/api/db/frames/${props.run.id}`).then(resp => {
      if (resp.ok) { resp.text().then(txt=>console.log(txt)) }
      else { resp.text().then(txt=>console.error(txt)) }
    })
  }, [])

  return (
    <div>{
        <Container className='mt-3'>
          <Button onClick={props.onLeave}>Go Back</Button>
          {
            props.run.config.cameras.map(cam=>(
              <Image fluid alt={cam.id} src={`/api/feed/viewer/${cam.id}`}/>
            ))
          }
        </Container>
      }</div>
  )
}
