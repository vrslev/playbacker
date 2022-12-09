export default function Placeholder(props: { text: string }) {
  return (
    <div class="grid h-full place-content-center text-gray-500">
      {props.text}
    </div>
  );
}
