interface OverlayProps {
  src: string;
  callback: Function;
}

export const Overlay = ({ src, callback }: OverlayProps) => {
  return (
    <div
      className="fixed top-0 left-0 right-0 bottom-0 backdrop-blur-md flex justify-center items-center"
      onClick={() => callback()}
    >
      <img className="max-w-[80%] max-h-[80%]" src={src} alt={src} />
    </div>
  );
};
