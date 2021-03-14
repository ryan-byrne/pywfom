import {useState} from 'react';

import EditCameras from './Edit';
import ConfigureCamera from './Configure';

import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Image from 'react-bootstrap/Image';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Modal from 'react-bootstrap/Modal';


export default function Cameras(props){

  const [editing, setEditing] = useState(false);
  const [configuring, setConfiguring] = useState(null);

  const handleThumbnail = (idx) => setConfiguring(idx);

  return (
    <div>
    {<Container className="text-center h-100">
        <Row className="align-items-center">
          {Object.keys(props.camerasConfig).map((key, idx) => {
            const cam = props.camerasConfig[key]
            return (
              <Col>
                <Image src={"api/feed/"+cam.id} fluid style={{cursor:'pointer'}}
                  onClick={()=>handleThumbnail(idx)}/>
              </Col>
            )
          })}
        </Row>
        <Row><Col>
          <Button onClick={()=>setEditing(true)}>
            {props.camerasConfig.length === 0 ? "Add Camera(s)" : "Edit Camera(s)"}
          </Button>
        </Col></Row>
      {
        !configuring ? null :
        <ConfigureCamera config={props.camerasConfig} camera={props.camerasConfig[configuring]}
          setConfig={props.setCamerasConfig}/>
      }
      <EditCameras cameras={props.camerasConfig} setCameras={props.setCamerasConfig}
        hideEditing={()=>setEditing(false)} editing={editing}/>
    </Container>}
    </div>
  )
}
