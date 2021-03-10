import {useState} from 'react';

import Edit from './Edit/Edit';

import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Image from 'react-bootstrap/Image';
import Col from 'react-bootstrap/Col';

export default function Cameras(){

  const [add, showAdd] = useState(false);
  const [cameras, setCameras] = useState([]);
  const [selected, setSelected] = useState(0);
  const handleAdd = (event) => showAdd(!add);

  const handleThumbnail = (event) => {

  }

  return (
    <Container className="text-center mt-3">
      {
        cameras.length === 0 ? null :
        cameras.map((cam, idx) => {
          return(
            <Col><Image fluid src={'/feed/'+idx.toString()}></Image></Col>
          )
        })
      }
      <Button className="m-3" onClick={()=>showAdd(true)}>
        { cameras.length === 0? "Add Camera(s)" : "Edit Camera(s)"}
      </Button>
      <Edit show={add} handleAdd={handleAdd} currentCameras={cameras}
        setCurrentCameras={setCameras}/>
    </Container>
  )
}
