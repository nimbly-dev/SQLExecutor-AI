import React, {
    ReactNode,
    useCallback,
    useEffect,
    useRef,
    useState
} from 'react';
import {
    TextField,
    MenuItem,
    ListSubheader,
    TextFieldProps,
    SelectChangeEvent,
    SelectProps as MUISelectProps
} from '@mui/material';

export type SelectOption = {
    value: string;
    label: string;
};

export interface DynamicScrollSelectFormFieldProps
    extends Omit<TextFieldProps, 'onChange' | 'value' | 'select'> {
    options: SelectOption[];
    value: string | string[];
    onChange: (value: string | string[]) => void;
    headerTitle?: string;
    multiple?: boolean;
    SelectProps?: Partial<MUISelectProps<unknown>>;
}


/**
 * A form field component that renders a Material-UI Select within a TextField.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {Array<{value: string, label: string}>} props.options - Array of options to display in the select
 * @param {string | string[]} props.value - Currently selected value(s)
 * @param {(value: string | string[]) => void} props.onChange - Callback fired when the value changes
 * @param {string} [props.headerTitle] - Optional title to display in the select menu header
 * @param {boolean} [props.multiple=false] - Whether multiple values can be selected
 * @param {MUISelectProps} [props.SelectProps] - Additional props to pass to the MUI Select component
 * @param {...TextFieldProps} props - Additional props to pass to the TextField component
 * 
 * @remarks
 * - Automatically closes when scrolling outside of viewport
 * - Supports single and multiple selection modes
 * - Can display an optional header in the dropdown menu
 * - Integrates with Material-UI's TextField and Select components
 * 
 * @example
 * ```tsx
 * <DynamicScrollFormField
 *   options={[
 *     { value: '1', label: 'Option 1' },
 *     { value: '2', label: 'Option 2' }
 *   ]}
 *   value="1"
 *   onChange={(value) => console.log(value)}
 *   headerTitle="Select an option"
 * />
 * ```
 */
const DynamicScrollFormField: React.FC<DynamicScrollSelectFormFieldProps> = ({
    options,
    value,
    onChange,
    headerTitle,
    multiple = false,
    SelectProps: additionalSelectProps,
    ...textFieldProps
}) => {
    const [open, setOpen] = useState<boolean>(false);
    const inputRef = useRef<HTMLElement | null>(null);
    const appBarHeight = 64;

    const handleChange = useCallback(
        (event: SelectChangeEvent<unknown>, child: ReactNode) => {
            onChange(event.target.value as string | string[]);
        },
        [onChange]
    );

    const handleScroll = useCallback(() => {
        if (!open || !inputRef.current || typeof inputRef.current.getBoundingClientRect !== 'function') return;
        const rect = inputRef.current.getBoundingClientRect();
        if (rect.top < appBarHeight || rect.bottom > window.innerHeight) {
            setOpen(false);
        }
    }, [open, appBarHeight]);

    useEffect(() => {
        if (open) {
            window.addEventListener('scroll', handleScroll, true);
        }
        return () => {
            window.removeEventListener('scroll', handleScroll, true);
        };
    }, [open, handleScroll]);

    const mergedMenuProps: MUISelectProps<unknown>['MenuProps'] = {
        disableScrollLock: true,
        anchorOrigin: {
            vertical: 'bottom',
            horizontal: 'left'
        },
        transformOrigin: {
            vertical: 'top',
            horizontal: 'left'
        },
        ...(additionalSelectProps?.MenuProps || {}),
        ...(headerTitle && {
            MenuListProps: {
                subheader: (
                    <ListSubheader
                        sx={{
                            py: 0,
                            lineHeight: '32px',
                            background: 'inherit',
                            zIndex: 1200
                        }}
                    >
                        {headerTitle}
                    </ListSubheader>
                )
            }
        })
    };

    const mergedSelectProps: MUISelectProps<unknown> = {
        multiple,
        value,
        onChange: handleChange,
        open,
        onOpen: () => setOpen(true),
        onClose: () => setOpen(false),
        MenuProps: mergedMenuProps,
        ...additionalSelectProps
    };

    return (
        <TextField
            select
            size="small"
            fullWidth
            margin="dense"
            ref={el => {
            if (el instanceof HTMLElement) {
                inputRef.current = el;
            }
            }}
            SelectProps={mergedSelectProps}
            sx={{
            '& .MuiInputBase-input': {
                fontSize: '0.8125rem', 
            }
            }}
            {...textFieldProps}
        >
            {options.map(({ value: optValue, label }) => (
            <MenuItem 
                key={optValue} 
                value={optValue}
                sx={{ 
                fontSize: '0.8125rem',  
                py: 0.5,              
                minHeight: '32px'
                }}
            >
                {label}
            </MenuItem>
            ))}
        </TextField>
    );
};

export default DynamicScrollFormField;
