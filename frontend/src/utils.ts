
  export const calculateSpinnerMessage = (progress: number) => {
    if (progress < 0) {
      return "";
    }
    return `${progress}%`;
  };

  export const scrollToBottom = (ref: React.MutableRefObject<HTMLDivElement | null>) => {
    ref?.current?.scrollIntoView({ behavior: "smooth" });
  };
