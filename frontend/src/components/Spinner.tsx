interface SpinnerProps {
  message: string;
}

export const Spinner = ({ message }: SpinnerProps) => {
  return (
    <div className="flex w-full justify-center p-4">
      <div>
        <div className="animate-spin">
          <img
            className="w-10 h-10 aspect-square"
            src="https://ia.leadoo.com/upload/images/bot_icon/WTYxNb0TNUeTcKL9.png"
            alt=""
          />
        </div>
        <div className="text-center">{message}</div>
      </div>
    </div>
  );
};
