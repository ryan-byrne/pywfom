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

  // State for storing camera configuration
  const [cameras, setCameras] = useState({});

  // Viewing states
  const [editing, showEditing] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState(null);

  useEffect(() => {
    fetch('/api/settings/cameras')
      .then(resp => {
        if (resp.ok){ return resp.json() }
        else { console.error(resp.message) } })
      .then(data => setCameras(data))
  },[])

  return (
    <div className="mt-3">
    {<Container className="text-center h-100">
        <Row className="align-items-center">
          {Object.keys(cameras).map((key, idx) => {
            const cam = cameras[key]
            return (
              <Col key={idx}>
                <Image src={"api/feed/"+cam.id} fluid style={{cursor:'pointer'}}
                  onClick={()=>setSelectedCamera(cam.id)} alt={cam.id}/>
              </Col>
            )
          })}
        </Row>
        <Row className="mt-3"><Col>
          <Button onClick={()=>showEditing(true)}>
            {Object.keys(cameras).length === 0 ? "Add Camera(s)" : "Edit Camera(s)"}
          </Button>
        </Col></Row>
      <EditCameras cameras={cameras} setCameras={setCameras}
        hideEditing={()=>showEditing(false)} show={editing}/>
      <ConfigureCamera cameras={cameras} setCameras={setCameras} selected={selectedCamera}
        onHide={()=>setSelectedCamera(null)}/>
    </Container>}
    </div>
  )
}
