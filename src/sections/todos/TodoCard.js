import { Button, Card,  Stack, Typography } from '@mui/material'
import useTodos from '../../hooks/useTodos';
import React from 'react'
import { useNavigate } from 'react-router-dom';
import PATHS from '../../routes/path';

const TodoCard = ({ todo }) => {
  const [_, { deleteTodo }] = useTodos();
  const navigate = useNavigate();
  
  const handleSelectTodo = () => navigate(`${PATHS.todo.detail(todo.id)}`);
  const handleDelete = (e) => {
    e.stopPropagation();
    deleteTodo(todo.id);
  }
  
  return (
    <Card onClick={handleSelectTodo} >
      <Stack p={2} alignItems='center' justifyContent='space-between' direction="row">
        <Typography variant='body2'>
          {todo.task}
        </Typography>
        <Button onClick={handleDelete} size="small" variant='outlined' color='error'>
          Supprimer
        </Button>
      </Stack>
    </Card>
  )
}

export default TodoCard