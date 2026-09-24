let counter = ref 0

let next_id prefix =
  incr counter;
  let id = Printf.sprintf "%s-%d" prefix !counter in
  print_endline ("allocated " ^ id);
  id
