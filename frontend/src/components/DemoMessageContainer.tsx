interface DemoMessageContainerProps {
  message: string;
  onClickCallback: Function
}

export const DemoMessageContainer = ({ message, onClickCallback }: DemoMessageContainerProps) => {
  return (
    <div className="justify-items-end grid h-fit w-full">
      <div className="flex items-end">
        <div onClick={() => onClickCallback()} className="cursor-pointer bg-secondary-200 shadow-secondary-300 text-secondary-100 ml-16 rounded-xl p-4 m-4 shadow-lg">
          <div>{message}</div>
        </div>
      </div>
    </div>
  );
};
