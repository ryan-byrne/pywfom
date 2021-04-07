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

  const setCameras = (data) => props.setConfig({...props.config, cameras:data});

  return (
    <div className="mt-3">
    {<Container className="text-center h-100">
        <Row className="align-items-center">
          {props.config.cameras.map((cam, idx) => {
            return (
              <Col key={idx}>
                <Image src={'/api/feed/'+cam.id} fluid style={{cursor:'pointer'}}
                  onClick={()=>setSelectedCamera(idx)} alt={idx}/>
              </Col>
            )
          })}
        </Row>
        <Row className="mt-3"><Col>
          <Button onClick={()=>showEditing(true)}>
            {Object.keys(props.config.cameras).length === 0 ? "Add Camera(s)" : "Edit Camera(s)"}
          </Button>
        </Col></Row>
      <EditCameras cameras={props.config.cameras} setCameras={setCameras}
        hideEditing={()=>showEditing(false)} show={editing}/>
      <ConfigureCamera setCameras={setCameras} cameras={props.config.cameras}
        onHide={()=>setSelectedCamera(null)} selected={selectedCamera}/>
    </Container>}
    </div>
  )
}
