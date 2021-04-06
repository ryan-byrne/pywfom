import {useState,useEffect} from 'react';

import EditCameras from './Edit';
import ConfigureCamera from './Configure';

import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Image from 'react-bootstrap/Image';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Tooltip from 'react-bootstrap/Tooltip';
import Overlay from 'react-bootstrap/Overlay';

export default function Cameras(props){

  // Viewing states
  const [editing, showEditing] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState(null);

  useEffect(() => {
    // Get System's current cameras
    fetch('/api/system/cameras')
      .then(resp => {
        if (resp.ok){ return resp.json() }
        else { console.error(resp) } })
      .then(data => props.setCameras(data))
  },[])

  return (
    <div className="mt-3">
    {<Container className="text-center h-100">
        <Row className="align-items-center">
          {props.cameras.map((cam, idx) => {
            return (
              <Col key={idx}>
                <Image src={"api/feed/"+idx} fluid style={{cursor:'pointer'}}
                  onClick={()=>setSelectedCamera(cam.id)} alt={cam.id}/>
              </Col>
            )
          })}
        </Row>
        <Row className="mt-3"><Col>
          <Button onClick={()=>showEditing(true)}>
            {Object.keys(props.cameras).length === 0 ? "Add Camera(s)" : "Edit Camera(s)"}
          </Button>
        </Col></Row>
      <EditCameras cameras={props.cameras} setCameras={props.setCameras}
        hideEditing={()=>showEditing(false)} show={editing}/>
      <ConfigureCamera cameras={props.cameras} setCameras={props.setCameras} selected={selectedCamera}
        onHide={()=>setSelectedCamera(null)}/>
    </Container>}
    </div>
  )
}
